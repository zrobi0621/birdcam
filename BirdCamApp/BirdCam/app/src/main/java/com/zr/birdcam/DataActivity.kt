package com.zr.birdcam

import android.content.Context
import android.os.Bundle
import android.util.Log
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.android.volley.Request
import com.android.volley.Response
import com.android.volley.toolbox.JsonArrayRequest
import com.android.volley.toolbox.Volley
import com.google.gson.Gson
import org.json.JSONArray
import org.json.JSONTokener

class DataActivity : AppCompatActivity() {

    private var layoutManager: RecyclerView.LayoutManager? = null
    private var adapter: RecyclerView.Adapter<RecyclerAdapter.ViewHolder>? = null
    private val myJsonList = arrayListOf<Measurement>()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_data)

        val ipPort = intent.getStringExtra("EXTRA_IP_PORT")

        // Instantiate the RequestQueue.
        val queue = Volley.newRequestQueue( this)
        val url = "http://$ipPort/measurements"

        // Request a string response from the provided URL.
        val jsonArrayRequest  = JsonArrayRequest(
                Request.Method.GET, url, null,
                Response.Listener{ response ->

                    val gson = Gson()

                    val jsonString = response.toString()
                    val jsonArray = JSONTokener(jsonString).nextValue() as JSONArray

                    for (i in 0 until jsonArray.length()) {
                        val jsonStr = jsonArray.getJSONObject(i).toString()
                        var measurement = gson.fromJson(jsonStr, Measurement::class.java)
                        myJsonList.add(measurement)
                    }

                    Log.d("succesAdapter", "Success: ${myJsonList.count()}")

                    layoutManager = LinearLayoutManager(this)

                    findViewById<RecyclerView>(R.id.recyclerView).layoutManager = layoutManager

                    myJsonList.reverse()
                    adapter = RecyclerAdapter(myJsonList)

                    findViewById<RecyclerView>(R.id.recyclerView).adapter = adapter
                    findViewById<RecyclerView>(R.id.recyclerView).adapter

                },
                Response.ErrorListener { error -> Log.d("Error.Response", error.toString())
                    Toast.makeText(applicationContext, "Error in DataGet", Toast.LENGTH_SHORT).show()
                })

        // Add the request to the RequestQueue.
        queue.add(jsonArrayRequest)
        Log.d("successAdapter", "Success: ${myJsonList.count()}")
    }
}