package com.zr.birdcam

import android.app.AlertDialog
import android.os.Bundle
import android.util.Log
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import com.android.volley.Request
import com.android.volley.Response
import com.android.volley.toolbox.JsonArrayRequest
import com.android.volley.toolbox.JsonObjectRequest
import com.android.volley.toolbox.Volley
import com.google.gson.Gson
import org.json.JSONArray
import org.json.JSONObject
import org.json.JSONTokener
import java.io.File
import java.time.LocalDateTime
import java.time.format.DateTimeFormatter


class SettingsActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_settings)

        try {
            this.supportActionBar!!.hide()
        } catch (e: NullPointerException) {
        }

        //  GET Settings
        getSettings()

        // Switches
        findViewById<Switch>(R.id.timeDetectionSwitch).setOnCheckedChangeListener(CompoundButton.OnCheckedChangeListener { buttonView, isChecked ->
            findViewById<Switch>(R.id.ldrDetectionSwitch).isChecked = !isChecked
        })

        findViewById<Switch>(R.id.ldrDetectionSwitch).setOnCheckedChangeListener(CompoundButton.OnCheckedChangeListener { buttonView, isChecked ->
            findViewById<Switch>(R.id.timeDetectionSwitch).isChecked = !isChecked
        })

        //  Export CSV Button
        findViewById<Button>(R.id.exportCsvButton).setOnClickListener{
            exportCSV()
        }

        //  Export JSON Button
        findViewById<Button>(R.id.exportJsonButton).setOnClickListener{
            exportJSON()
        }
    }

    override fun onBackPressed() {
        val builder1 = AlertDialog.Builder(this)
        builder1.setMessage("Do you want to save Settings?")
        builder1.setCancelable(true)

        builder1.setPositiveButton(
                "Yes"
        ) { dialog, id -> dialog.cancel()
            Toast.makeText(applicationContext, "Settings saved", Toast.LENGTH_SHORT).show()
            postSettings()
            super.onBackPressed()
        }

        builder1.setNegativeButton(
                "No"
        ) { dialog, id -> dialog.cancel()
            super.onBackPressed()}

        val alert1 = builder1.create()
        alert1.show()
    }

    private fun getSettings() {
        val ipPort = intent.getStringExtra("EXTRA_IP_PORT")

        val emailSendingSwitch = findViewById<Switch>(R.id.emailSendingSwitch)
        val emailTo1Text = findViewById<EditText>(R.id.emailTo1)
        val emailTo2Text = findViewById<EditText>(R.id.emailTo2)
        val emailTo3Text = findViewById<EditText>(R.id.emailTo3)
        val dailyMaxEmailsText = findViewById<EditText>(R.id.dailyMaxEmails)
        val timeBetweenEmailsText = findViewById<EditText>(R.id.timeBetweenEmails)
        val timeDetectionSwitch = findViewById<Switch>(R.id.timeDetectionSwitch)
        val ldrDetectionSwitch = findViewById<Switch>(R.id.ldrDetectionSwitch)
        val detectionTimeFromText = findViewById<EditText>(R.id.detectionTimeFrom)
        val detectionTimeToText = findViewById<EditText>(R.id.detectionTimeTo)
        val detectionLDRFromText = findViewById<EditText>(R.id.detectionLDRFrom)
        val detectionLDRToText = findViewById<EditText>(R.id.detectionLDRTo)


        // Instantiate the RequestQueue.
        val queue = Volley.newRequestQueue(this)
        val url = "http://$ipPort/settings"

        // Request a string response from the provided URL.
        val jsonObjectRequest  = JsonObjectRequest(
                Request.Method.GET, url, null,
                Response.Listener{ response ->

                    Log.d("Settings", "GetSettings OK")

                    val isEmailSendingActive = response.get("isEmailSendingActive") as Boolean
                    var emailTo1 = response.get("emailTo1")
                    var emailTo2 = response.get("emailTo2")
                    var emailTo3 = response.get("emailTo3")
                    val dailyMaxEmails = response.get("maxDailyEmail")
                    val timeBetweenEmails = response.get("timeBetweenEmails")
                    val isDetectionWithTimeActive = response.get("isDetectionWithTimeActive") as Boolean
                    val isDetectionWithLDR = response.get("isDetectionWithLDR") as Boolean
                    val detectionTimeFrom = response.get("detectionTimeFrom")
                    val detectionTimeTo = response.get("detectionTimeTo")
                    val detectionLDRFrom = response.get("detectionLDRFrom")
                    val detectionLDRTo = response.get("detectionLDRTo")

                    emailSendingSwitch.isChecked = isEmailSendingActive

                    if(emailTo1 == "null")
                        emailTo1 = ""
                    if(emailTo2 == "null")
                        emailTo2 = ""
                    if(emailTo3 == "null")
                        emailTo3 = ""

                    emailTo1Text.setText(emailTo1.toString())
                    emailTo2Text.setText(emailTo2.toString())
                    emailTo3Text.setText(emailTo3.toString())
                    dailyMaxEmailsText.setText(dailyMaxEmails.toString())
                    timeBetweenEmailsText.setText(timeBetweenEmails.toString())
                    timeDetectionSwitch.isChecked = isDetectionWithTimeActive
                    ldrDetectionSwitch.isChecked = isDetectionWithLDR
                    detectionTimeFromText.setText(detectionTimeFrom.toString())
                    detectionTimeToText.setText(detectionTimeTo.toString())
                    detectionLDRFromText.setText(detectionLDRFrom.toString())
                    detectionLDRToText.setText(detectionLDRTo.toString())
                },
                Response.ErrorListener { error -> Log.d("Error.Response", error.toString())
                    emailSendingSwitch.isChecked = false
                    emailTo1Text.setText("")
                    emailTo2Text.setText("")
                    emailTo3Text.setText("")
                    dailyMaxEmailsText.setText("")
                    timeBetweenEmailsText.setText("")
                    timeDetectionSwitch.isChecked = false
                    ldrDetectionSwitch.isChecked = false
                    detectionTimeFromText.setText("")
                    detectionTimeToText.setText("")
                    detectionLDRFromText.setText("")
                    detectionLDRToText.setText("")
                })
        // Add the request to the RequestQueue.
        queue.add(jsonObjectRequest )
    }

    private fun postSettings() {
        val ipPort = intent.getStringExtra("EXTRA_IP_PORT")

        val emailSendingSwitch = findViewById<Switch>(R.id.emailSendingSwitch)
        val emailTo1Text = findViewById<EditText>(R.id.emailTo1)
        val emailTo2Text = findViewById<EditText>(R.id.emailTo2)
        val emailTo3Text = findViewById<EditText>(R.id.emailTo3)
        val dailyMaxEmailsText = findViewById<EditText>(R.id.dailyMaxEmails)
        val timeBetweenEmailsText = findViewById<EditText>(R.id.timeBetweenEmails)
        val timeDetectionSwitch = findViewById<Switch>(R.id.timeDetectionSwitch)
        val ldrDetectionSwitch = findViewById<Switch>(R.id.ldrDetectionSwitch)
        val detectionTimeFromText = findViewById<EditText>(R.id.detectionTimeFrom)
        val detectionTimeToText = findViewById<EditText>(R.id.detectionTimeTo)
        val detectionLDRFromText = findViewById<EditText>(R.id.detectionLDRFrom)
        val detectionLDRToText = findViewById<EditText>(R.id.detectionLDRTo)

        // Instantiate the RequestQueue.
        val queue = Volley.newRequestQueue(this)
        val url = "http://$ipPort/settings"

        val jsonobj = JSONObject()

        jsonobj.put("isEmailSendingActive", emailSendingSwitch.isChecked)
        jsonobj.put("emailTo1", emailTo1Text.text)
        jsonobj.put("emailTo2", emailTo2Text.text)
        jsonobj.put("emailTo3", emailTo3Text.text)
        jsonobj.put("maxDailyEmail",dailyMaxEmailsText.text)
        jsonobj.put("timeBetweenEmails",timeBetweenEmailsText.text)
        jsonobj.put("isDetectionWithTimeActive", timeDetectionSwitch.isChecked)
        jsonobj.put("isDetectionWithLDR", ldrDetectionSwitch.isChecked)
        jsonobj.put("detectionTimeFrom", detectionTimeFromText.text)
        jsonobj.put("detectionTimeTo", detectionTimeToText.text)
        jsonobj.put("detectionLDRFrom", detectionLDRFromText.text)
        jsonobj.put("detectionLDRTo", detectionLDRToText.text)

        val que = Volley.newRequestQueue(this)
        val req = JsonObjectRequest(Request.Method.POST, url, jsonobj,
                Response.Listener {
                    response ->
                    println("POST OK")
                }, Response.ErrorListener {
            Log.d("POST","Error in POST")
                Toast.makeText(applicationContext, "Settings Saving Error", Toast.LENGTH_SHORT).show()})
        que.add(req)
    }

    private fun exportJSON()
    {
        val ipPort = intent.getStringExtra("EXTRA_IP_PORT")

        // Instantiate the RequestQueue.
        val queue = Volley.newRequestQueue(this)
        val url = "http://$ipPort/measurements"

        // Request a string response from the provided URL.
        val jsonArrayRequest  = JsonArrayRequest(
                Request.Method.GET, url, null,
                Response.Listener{ response ->

                    val myJsonList : MutableList<Measurement> = mutableListOf()
                    val gson = Gson()

                    val jsonString = response.toString()

                    val current = LocalDateTime.now()
                    val formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd-HH-mm-ss")
                    val date = current.format(formatter)

                    val path = applicationContext!!.getExternalFilesDir(null)
                    File("$path/BirdCamJSONExport-$date.json").appendText(jsonString)

                    Toast.makeText(applicationContext, "Exported: $path", Toast.LENGTH_SHORT).show()
                },
                Response.ErrorListener { error -> Log.d("Error.Response", error.toString())
                    Toast.makeText(applicationContext, "Error in JSONExport", Toast.LENGTH_SHORT).show()
                })

        // Add the request to the RequestQueue.
        queue.add(jsonArrayRequest)
    }

    private fun exportCSV() {
        val ipPort = intent.getStringExtra("EXTRA_IP_PORT")

        // Instantiate the RequestQueue.
        val queue = Volley.newRequestQueue(this)
        val url = "http://$ipPort/measurements"

        // Request a string response from the provided URL.
        val jsonArrayRequest  = JsonArrayRequest(
            Request.Method.GET, url, null,
            Response.Listener{ response ->

                val myJsonList : MutableList<Measurement> = mutableListOf()
                val gson = Gson()

                val jsonString = response.toString()
                val jsonArray = JSONTokener(jsonString).nextValue() as JSONArray

                val current = LocalDateTime.now()
                val formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd-HH-mm-ss")
                val date = current.format(formatter)

                val headerText = "dateTime,minTemp,maxTemp,minHumidity,maxHumidity\n"

                val path = applicationContext!!.getExternalFilesDir(null)
                File("$path/BirdCamCSVExport-$date.csv").appendText(headerText)

                for (i in 0 until jsonArray.length()) {
                    val jsonStr = jsonArray.getJSONObject(i).toString()
                    var measurement = gson.fromJson(jsonStr, Measurement::class.java)
                    myJsonList.add(measurement)
                }

                for (item in myJsonList) {
                    File("$path/BirdCamCSVExport-$date.csv").appendText("${item.datetime},${item.minTemp},${item.maxTemp},${item.minHumidity},${item.maxHumidity}\n")
                }

                Toast.makeText(applicationContext, "Exported: $path", Toast.LENGTH_SHORT).show()
            },
            Response.ErrorListener { error -> Log.d("Error.Response", error.toString())
                Toast.makeText(applicationContext, "Error in CSVExport", Toast.LENGTH_SHORT).show()
            })

        // Add the request to the RequestQueue.
        queue.add(jsonArrayRequest)
    }
}