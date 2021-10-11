package com.zr.birdcam

import android.util.Log
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView

class RecyclerAdapter(private val measurements: ArrayList<Measurement>) : RecyclerView.Adapter<RecyclerAdapter.ViewHolder>(){

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): RecyclerAdapter.ViewHolder {
        val v = LayoutInflater.from(parent.context).inflate(R.layout.card_layout,parent,false)
        return ViewHolder(v)
    }

    override fun getItemCount(): Int {
        return measurements.count()
    }

    override fun onBindViewHolder(holder: RecyclerAdapter.ViewHolder, position: Int) {
        holder.dateText.text = measurements[position].datetime.dropLast(9)
        holder.tempText.text = ": (min - max): ${measurements[position].minTemp}°C - ${measurements[position].maxTemp}°C"
        holder.humidityText.text = ": (min - max): ${measurements[position].minHumidity}% - ${measurements[position].maxHumidity}%"
    }

    inner class ViewHolder(itemView: View): RecyclerView.ViewHolder(itemView){
        var dateText: TextView
        var tempText: TextView
        var humidityText: TextView

        init{
            dateText = itemView.findViewById(R.id.dateText)
            tempText = itemView.findViewById(R.id.tempText)
            humidityText = itemView.findViewById(R.id.humidityText)
        }
    }
}