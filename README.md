# AeroLeads Assignment Project

This repository contains the solution for a multi-faceted assignment focusing on **web scraping**, **API integration**, and **AI content generation**. The goal is to demonstrate practical application of various modern technologies and problem-solving skills, even when faced with real-world obstacles like login walls and API limits.

---

## 🎯 Task 1: LinkedIn Profile Data Scraper 🌐

### **Objective**
Develop a script to **scrape data from 20 random LinkedIn profile URLs** (e.g., `linkedin.com/in/xxxxxx`) and save the extracted profile information into a **CSV file**.

### **Key Challenges & Approaches**
* **LinkedIn Login Wall:** Accessing profile data without being logged in is the primary hurdle.
    * **Proposed Solution:** Utilize a **test LinkedIn account** for automated login.
    * **Strategy:** Try navigating via Google search (enter the URL in Google and open the first link) to potentially bypass some direct access restrictions.
* **Automation:** Employ **Selenium** with **Chrome drivers** to handle the login and navigation.
* **Evasion Techniques:** Implement **different browser headers and user agents**. Consider using **rotating proxies or residential proxies** to mitigate IP-based blocking.
* **Alternative Data Sources:** Explore scraping other sites that might aggregate or display public LinkedIn data.

> **Note:** Successful completion of the entire task is not mandatory. The effort and ingenuity applied to overcoming the obstacles are the main focus.

---

## 📞 Task 2: Autodialer Ruby on Rails Application

### **Objective**
Build a small **Ruby on Rails application** named **`Autodialer`** that can automatically call a list of 100 random Indian phone numbers, one by one.

### **Core Functionality**
1.  **Phone Number Management:** Implement a small interface that allows users to **copy/paste 100 phone numbers** or **upload a file** containing the list.
2.  **Automated Dialing:** Call the numbers sequentially using a telephony API.
3.  **Logging and Reporting:** Display a clear **log** showing call status, such as:
    * Calls **picked up**.
    * Calls **failed** or **not answered**.

### **Integration & Enhancements**
* **Telephony API:** Utilize the **Twilio API** or explore other viable alternatives for programmatic calling.
* **AI Command Prompt:** Integrate an AI feature to allow users to initiate calls using natural language commands, such as:
    > "make a call to XXXXXX number"
* **AI Voice:** Incorporate an **AI-generated voice** for the outgoing calls.

> **Testing Guidance:** **Crucially, for testing purposes, use 1800 XXX XXXX numbers (toll-free/dummy numbers) only. Do NOT call real people!**

---

## 📝 Task 3: AI-Generated Blog Content and Integration

### **Objective**
Generate **10 articles** on various programming topics using AI tools and integrate them into the `Autodialer` application under a dedicated `/blog` route.

### **AI Integration Details**
* **Content Generation Prompt:** Implement an **AI prompt** feature where a user can input a list of titles along with some brief context/details, and the system will automatically generate the full article content.
* **API Usage:** Leverage APIs from advanced language models:
    * **Perplexity PRO API**
    * **Gemini API**
    * **ChatGPT API**
* **Implementation:** The application will pass the specified titles and the user's prompt to the chosen API to receive the article body, which is then inserted into the application's blog storage.

---

## 🛠️ Technology Stack (Suggested)

| Component | Technology/Tool | Purpose |
| :--- | :--- | :--- |
| **Scraping** | Python (or preferred language), Selenium, Chrome Drivers | Web automation and data extraction |
| **Application** | Ruby on Rails | Web application framework for Autodialer and Blog |
| **Calling API** | Twilio, or alternatives | Programmatic phone call execution |
| **AI Generation** | Gemini API, Perplexity PRO API, or ChatGPT API | Generating call commands (Task 2) and Blog Content (Task 3) |
| **Data Storage** | CSV (for Task 1 output), Database (for Task 2/3 app data) | Storing scraped data and application content/logs |

---

## 🚀 Getting Started

Instructions on setting up the environment, installing dependencies, and running the application will be provided here.
