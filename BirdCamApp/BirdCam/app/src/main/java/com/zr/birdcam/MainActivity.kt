package com.zr.birdcam

import android.content.Context
import android.content.Intent
import android.os.Bundle
import android.util.Log
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.appcompat.app.AppCompatDelegate
import com.android.volley.Request
import com.android.volley.Response
import com.android.volley.toolbox.JsonObjectRequest
import com.android.volley.toolbox.Volley
import com.faizkhan.mjpegviewer.MjpegView
import org.json.JSONObject

class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        AppCompatDelegate.setDefaultNightMode(AppCompatDelegate.MODE_NIGHT_NO)
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val sharedPref = this?.getPreferences(Context.MODE_PRIVATE)
        val connected = sharedPref.getString("connected","false")

        if(connected.equals("true"))
        {
            connect()
        }

        //  CONNECT BUTTON
        findViewById<Button>(R.id.connectButton).setOnClickListener{
            val sharedPref = this?.getPreferences(Context.MODE_PRIVATE)
            val connected = sharedPref.getString("connected","false")

            connect()
        }

        //  DATA
        findViewById<Button>(R.id.dataButton).setOnClickListener{
            openData()
        }

        //  SETTINGS
        findViewById<Button>(R.id.settingsButton).setOnClickListener{
            openSettings()
        }
    }

    override fun onBackPressed() {
        super.onBackPressed()

        val sharedPref = this?.getPreferences(Context.MODE_PRIVATE) ?: return
        with (sharedPref.edit()) {
            putString("connected","false")
            apply()
        }

        android.os.Process.killProcess(android.os.Process.myPid())
    }

    private fun connect()
    {
        val server = findViewById<EditText>(R.id.serverText)

        var serverIPPort = "192.168.1.99:9000"
        serverIPPort = server.text.toString()
        val streamingServerIP = serverIPPort.dropLast(5)
        var streamingServerPORT = serverIPPort.takeLast(4).toInt()
        streamingServerPORT += 1
        val streamingServerIPPORT = streamingServerIP + ":" + streamingServerPORT

        val sharedPref = this?.getPreferences(Context.MODE_PRIVATE) ?: return
        with (sharedPref.edit()) {
            putString("serverIPPort",serverIPPort)
            putString("streamingServerIPPort",streamingServerIPPORT)
            putString("connected","true")
            apply()
        }

        loadServerStatus()

        Thread.sleep(2000)

        // LIVE CAM
        var view: MjpegView? = null
        view = findViewById(R.id.liveCamImage)
        view!!.isAdjustHeight = true
        view!!.mode1 = MjpegView.MODE_FIT_WIDTH
        view!!.setUrl("http://$streamingServerIPPORT/stream.mjpg")
        view!!.isRecycleBitmap1 = true


        if(getStreamingInfo() == false)
        {
            Thread.sleep(1000)
            view!!.startStream()
        }
        else
            view!!.startStream()

        // Run in background to check the App is open
        Thread(Runnable {
            while (true)
            {
                Thread.sleep(20000)
                getStreamingInfo()
            }
        }).start()
    }

    private fun getStreamingInfo(): Boolean{
        var isLiveCamActive = false

        val sharedPref = this?.getPreferences(Context.MODE_PRIVATE)
        val serverIPPort = sharedPref.getString("serverIPPort","192.168.1.99:9000")

        // Instantiate the RequestQueue.
        val queue = Volley.newRequestQueue(this)
        val url = "http://$serverIPPort/streaminginfo"

        // Request a string response from the provided URL.
        val jsonObjectRequest  = JsonObjectRequest(
                Request.Method.GET, url, null,
                Response.Listener{ response ->

                     response.get("isLiveCamActive") as Boolean

                },
                Response.ErrorListener { error -> Log.d("Error.Response", error.toString())
                    isLiveCamActive = false
                })

        // Add the request to the RequestQueue.
        queue.add(jsonObjectRequest )

        return isLiveCamActive
    }

    private fun openData()
    {
        val sharedPref = this?.getPreferences(Context.MODE_PRIVATE)
        val serverIPPort = sharedPref.getString("serverIPPort","192.168.1.99:9000")

        val intent = Intent(baseContext, DataActivity::class.java)
        intent.putExtra("EXTRA_IP_PORT", serverIPPort)
        startActivity(intent)
    }

    private fun openSettings()
    {
        val sharedPref = this?.getPreferences(Context.MODE_PRIVATE)
        val serverIPPort = sharedPref.getString("serverIPPort","192.168.1.99:9000")

        val intent = Intent(baseContext, SettingsActivity::class.java)
        intent.putExtra("EXTRA_IP_PORT", serverIPPort)
        startActivity(intent)
    }

    private fun loadServerStatus() {
        val cpuTextView = findViewById<TextView>(R.id.cpuTempText)
        val ldrTextView = findViewById<TextView>(R.id.ldrText)
        val tempTextView = findViewById<TextView>(R.id.temperatureText)
        val humidityTextView = findViewById<TextView>(R.id.humidityText)

        val sharedPref = this?.getPreferences(Context.MODE_PRIVATE)
        val serverIPPort = sharedPref.getString("serverIPPort","192.168.1.99:9000")

        // Instantiate the RequestQueue.
        val queue = Volley.newRequestQueue(this)
        val url = "http://$serverIPPort/data"

            // Request a string response from the provided URL.
            val jsonObjectRequest  = JsonObjectRequest(
                    Request.Method.GET, url, null,
                    Response.Listener{ response ->

                        val cpuTemp = response.get("cputemp")
                        val ldr = response.get("ldr")
                        val humidity = response.get("humidity")
                        val temperature = response.get("temperature")

                        cpuTextView.text = cpuTemp.toString() + " °C"
                        ldrTextView.text = ldr.toString().take(3)
                        humidityTextView.text = humidity.toString() + " %"
                        tempTextView.text = temperature.toString() + " °C"
                    },
                    Response.ErrorListener { error -> Log.d("Error.Response", error.toString())
                        loadServerStatus()
                    })

            // Add the request to the RequestQueue.
            queue.add(jsonObjectRequest )
    }
}