# I2P(I) 2025 Final Project: Monster Go

Final Project Template for National Tsing Hua University Introduction to Programming (I) 114 Fall

## Author
**114062107 文柏鈞**

## Setup Project
1. (Recommended) Install Python 3.12.x (We use 3.12.8) from the official Python website and create virtual environment
    ```bash
    python3.12 -m venv venv
    
    # On mac/linux
    source venv/bin/activate
    
    # On windows
    ./venv/Scripts/activate
    ```
2. (Required) Install the required libraries
    ```bash
    pip install -r requirements.txt
    ```
3. Run the game:
    ```bash
    python main.py
    ```
    
## Setup Server for Online Play

1. Run The server
    ```bash
    python server.py
    ```
    
2. Run your client
    ```bash
    python main.py --online
    ```
    
You can run multiple client on a single computer. 

Although it's not required, you may also share the server with your friends by configuring the ip address instead of using localhost. 
    
