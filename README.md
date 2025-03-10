# YOLO-Object-Counting
This repository contains a set of three object detection and counting programs designed for NVIDIA Jetson devices with 10-inch displays. These programs are optimized for real-time industrial applications, providing an intuitive graphical user interface (GUI) and leveraging YOLO deep learning models (both pre-trained and custom-trained).  


Each program is designed to count up to two different object types simultaneously, making them ideal for scenarios requiring real-time monitoring, such as production lines, warehouse tracking, and automated logistics systems.  

----------------------------------------------------------------------

🚀 KEY FEATURES 

✅ Advanced Graphical User Interface (GUI)  
Fully developed GUI optimized for 10-inch screens.
Displays real-time detection output along with essential object counting details.
Interactive buttons for Start, Restart, and Pause to control the counting process dynamically.
Integrated menu section for easy navigation.
Error handling system that logs issues and updates automatically every day.

✅ Real-Time Object Counting with YOLO  
Uses YOLO (You Only Look Once) deep learning models for accurate object detection and tracking.
Supports both pre-trained models and custom-trained YOLO models for flexibility.
Efficiently tracks and counts two different object types at the same time.  

✅ Modular and Customizable
The programs are interchangeable, allowing users to combine, modify, or swap features to suit specific industrial needs.
Different configurations for single-direction or bidirectional counting.  

✅ Data Storage & Error Logging  
The first two programs store all processing data directly into a database.
The GPIO-integrated version utilizes tracking files, which can be accessed anytime for auditing and troubleshooting.
Daily auto-updating log files keep track of errors and ensure reliable performance monitoring.  

✅ GPIO Integration for Hardware Interaction  
The third program in the repository supports direct interaction with external hardware (e.g., conveyor belts).
Ideal for automated sorting systems or production lines requiring direct machine communication.  

----------------------------------------------------------------------

📂 PROGRAM STRUCTURE & BREAKDOWN  

1️⃣ "2 objects detected IN"  

  📌 Description:  
    Designed to count objects moving in one direction (entry).  
    Runs on Jetson devices and is optimized for real-time industrial production use.  
    Stores all processed data in a database for easy retrieval and analysis.  

  📌 Ideal Use Cases:  
    Assembly lines tracking incoming components.  
    Warehouse monitoring for items being placed into storage.  
    Quality control stations where only incoming items are relevant.  


2️⃣ "2 objects detected IN & OUT"  

  📌 Description:  
    An extension of the first program that counts objects moving in both directions (entry & exit).  
    Maintains the same GUI, error tracking, and database storage system.  

  📌 Ideal Use Cases:  
    Logistics centers tracking both inbound and outbound shipments.  
    Production lines with separate input and output verification.  
    Retail inventory tracking, monitoring stock movement.  


3️⃣ "Integrated with GPIO"  

  📌 Description:
    Includes GPIO integration, allowing direct communication with hardware (e.g., conveyor belts, robotic arms, or sorting mechanisms).  
    Unlike the other two programs, it does not store data in a database but instead generates tracking files that can be accessed anytime.   

  📌 Ideal Use Cases:  
    Automated conveyor systems for sorting and classifying products.  
    Manufacturing environments where object tracking requires hardware interaction.  
    Smart factories using sensors and actuators to optimize workflow.  

------------------------------------------------------------

🔧 CUSTOMIZATION & EXTENSIBILITY  
- All three programs are designed with modular components, making it easy to:  
- Swap detection models.
- Adjust counting logic for specific industrial needs.  
- Combine features from multiple programs to create a fully tailored solution.
  
-------------------------------------------------------------

💡 WHY THIS SYSTEM?  
This project was developed to address real-world industrial needs, providing a flexible, accurate, and easy-to-use object counting system. By combining real-time deep learning-based detection, an intuitive GUI, and hardware interaction capabilities, it offers an adaptable solution for smart factories, automated warehouses, and production monitoring.

-------------------------------------------------------------

📌 WANT TO CUSTOMIZE IT FOR YOUR SPECIFIC USE CASE?    
All features are modular and can be adjusted to fit your needs. Start building your own YOLO-powered counting system today! 🚀
