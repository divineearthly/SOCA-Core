package com.soca.assistant

import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {
    private lateinit var inputText: EditText
    private lateinit var outputText: TextView
    private lateinit var askButton: Button
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        
        inputText = findViewById(R.id.inputText)
        outputText = findViewById(R.id.outputText)
        askButton = findViewById(R.id.askButton)
        
        askButton.setOnClickListener {
            val query = inputText.text.toString()
            if (query.isNotEmpty()) {
                outputText.text = "Processing: $query\n\n"
                // In production, this would call the SOCA runtime
                outputText.append("Recommended: Rice for kharif season")
            }
        }
    }
}
