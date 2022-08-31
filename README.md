<br />
<h3 align="center">Titi Bookstore Manager</h3>
  <p align="center">
    This is a bookstore/cafe transactions GUI Python manager app customly designed<br>for my mother's bookstore.
    <br />
    <br />
    <br />
  </p>
</div>
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

This project was initiated in December 2021 and toke 9 months to complete, and its aim was to manage the transactions of my mother's cafe/bookstore. The problem that this program solves was calculating the wifi charges for each customer simultaneously. Made in python using the tkinter module for the GUI, and pandas, json, csv modules for storing neccessary data.

![image](https://github.com/Mohamed-ElGemeie/bookstore-manager-GUI/blob/main/imgs/report.PNG?raw=true)
<p align="right">(<a href="#top">back to top</a>)</p>



### Built With

* [Python 3.10.4](https://www.python.org/downloads/release/python-3104/)
* [MySQL 8.0.30](https://dev.mysql.com/downloads/)

<!-- GETTING STARTED -->
## Getting Started

First you need to have all the privelages to any MySQL user (could be done in MySQL workbench), and download all the files from Repo [code](https://github.com/Mohamed-ElGemeie/bookstore-manager-GUI/tree/main/code) and [data-base](https://github.com/Mohamed-ElGemeie/bookstore-manager-GUI/tree/main/data-base)

### Prerequisites

* Pip installations - Currentely used working versions
  ```sh
  pip install pandas (1.4.2)
  pip install numpy (1.22.3)
  pip install tk (0.1.0)
  pip install SQLAlchemy (1.4.39)
  pip install mysql-connector-python (8.0.29)
  ```
* Python Builtins
    ```sh
    datetime, json, csv, dateutil, time, os 
    ```
* MySQL
    ```sh
    MySQL server running with access to admin rights.
    Empty Database to import the data-base tables and content.
    ```
### Installation

1. Set up and run a SQL server instance, check [dev.mysql.com](https://dev.mysql.com/doc/workbench/en/wb-mysql-connections-new.html) for more information.
2. Download the [data-base](https://github.com/Mohamed-ElGemeie/bookstore-manager-GUI/tree/main/data-base) .sql files and import them into your desired database using MySQL-workbench (8.0) CE
   * ```open instance connection--> server tab--> Data Import--> import from dump folder```
   * Then select the "data-base" file that contains all the .sql files.
   * Make sure you downloaded each .sql file to avoid any major errors.
   * Make sure the connection is always on while the excution of the program.
3. Download [code](https://github.com/Mohamed-ElGemeie/bookstore-manager-GUI/tree/main/code) and place all the files in the same directory.
    * <b>book_gui_pager.py</b> is the main driver and the only file that should be run.
    * <b>db_open.py</b> handles the access to the MySQL database and shouldn't be run.
    * <b>config.json</b> holds all last date the program was run on and counters for each type of transaction. DO NOT change the keys of this file.
   
<p align="right">(<a href="#top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage

This project can make session (Wifi charged) and take-away(Not Wifi charged) transactions which both were a custom specification by the owner of the cafe.<br>
### Features
* Create session transactions.
* Create quick-takeaway transactions.
* Create books and printed paper transactions.
* Record stock transaction and automatically change the stock in accordance to the customer's order.
* Maintain multiple sessions and charge Wifi for each one.
* Display a recipt for the barista with all the details about the transaction.
* Create a report on any date containing important features like
    * Profit
    * Stock revenue 
    * Transaction revenue 
    * Wifi charges revenue
* Store all the above information to a database for easy analysis later on using SQL.

### Feature details
* One quantity of printed paper charges for 0.75 
* Take-away transactions aren't charged with Wifi
* All sessions have to have a wifi charge.
    * Each hour is charged with 5 pounds. Wifi charge max is 25
    * Sessions that don't have any orders are charged with 10 for the first hour and at max with 30 pounds for the wifi charge.
* Books and printed paper transactions are saved to the books table unlike all other transactions.
* Any stock transactions have to have changed the stock table in order to be recorded.
* You can have a stock transaction with zero as the payment price.
* Take-away and in-store items have different prices on the menu.
* Each counter for the  stock, take-away, session are reset when the program is opened on a day different from the last date the program was open on. This ensures unique IDs for each transaction.

![image](https://github.com/Mohamed-ElGemeie/bookstore-manager-GUI/blob/main/imgs/session_order.PNG?raw=true)
<p align="right">(<a href="#top">back to top</a>)</p>

<!-- CONTRIBUTING -->
## Contributing

If you have any suggestions that would make this system better, please fork the repo and create a pull request. I am very intrested in any other improvments any one could add while maintaing the use of the tkinter module.

1. Fork the Project
2. Create your Feature Branch 
3. Commit your Changes 
4. Push to the Branch 
5. Open a Pull Request

<p align="right">(<a href="#top">back to top</a>)</p>


<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE.txt` for more information.


<!-- CONTACT -->
## Contact
Mohamed Galal Elgemeie [@Linkedin](https://www.linkedin.com/in/mohamed-elgemeie) 
<br>

If you are interested in a custom version with additional features or require any help with this software<br>please contant me through my email.<br><br>
Email: mgalal2002@outlook.com<br>

Project Link: https://github.com/Mohamed-ElGemeie/bookstore-manager-GUI
<p align="right">(<a href="#top">back to top</a>)</p>

