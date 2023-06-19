<br />
<h3 align="center">Titi Bookstore Manager</h3>
  <p align="center">
    Bookstore/Cafe GUI Python transaction manager app customly designed<br>for my mother's bookstore.
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

First you need to have all the privelages to any MySQL user (could be done in MySQL workbench), and download all the files from the [Repo](https://github.com/Mohamed-ElGemeie/bookstore-manager-GUI/tree/main)

### Prerequisites

* Check currentely used working [packages](https://github.com/Mohamed-ElGemeie/bookstore-manager-GUI/blob/main/requirements.txt) installed using Pip

* Python Builtins
    ```sh
    tkinter, datetime, json, csv, dateutil, time, os 
    ```
* MySQL
    ```sh
    MySQL server running with access to admin rights.
    Setup connection to import the data-base tables and content.
    ```
### Installation

1. Set up and run a SQL server instance, check [dev.mysql.com](https://dev.mysql.com/doc/workbench/en/wb-mysql-connections-new.html) for more information.

2. Open the [self-contained-file](https://github.com/Mohamed-ElGemeie/bookstore-manager-GUI/blob/main/db/init_db.sql) and import it into your desired database using MySQL-workbench (8.0) CE
   * ```open instance connection--> server tab--> Data Import--> import from Self-contained-file```
   * Then select the [self-contained-file](https://github.com/Mohamed-ElGemeie/bookstore-manager-GUI/blob/main/db/init_db.sql) as your dir.
   * Make sure the connection is always online while the excution of the program.
   
3. Modify [src\config\\_db_config.json](https://github.com/Mohamed-ElGemeie/bookstore-manager-GUI/blob/main/src/config/_db_config.json) with the following:
    - Rename the .json file to "db_config.json"
    - Change the fields inside the .json file to the following:
    
        ``` 
        {
        "sql_server_passcode": "The password you assigned to access your MySQL server connection",
        "port": The port your specified for your connection,
        "db_name": "db_bookstore",
        "user":"The name of the current machine's user, probably (root)",
        "host":"The name of your connection's host, probably (localhost)"
        }
        ```
4. Open MySQL-workbench and modify the Items table inside the db_bookstore schema, to add your own custom menu.
   
<p align="right">(<a href="#top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage

This project can make session (Wifi charged) and take-away (Not Wifi charged) transactions which both were a custom specification by the owner of the cafe.<br>

### Features
* Create session transactions.

* Create quick-takeaway transactions.

* Create books and printed paper transactions.

* Maintain multiple sessions and charge Wifi for each one.

* Display a recipt for the barista with all the details about the transaction.

* Create a report on any date containing important features like
    * Transaction Profit
    * Transaction Count 
    * Filter by day-range 
    * Detailed queries about certain transation types
    
* Store all the above information to a database for easy analysis later on using SQL.

### Feature details

* One quantity of printed paper charges for 0.75 

* Take-away transactions aren't charged with Wifi

* All sessions have to have a wifi charge.
    * Each hour is charged with 5 pounds. Wifi charge max is 25
    * Wifi charge could be modified on checkout
    * A Session transaction can only hold a wifi charge and no items

* Take-away and in-store items have different prices on the menu.

* The time of a session's initiation, session's end, takeaway initiationis all recoreded.

![image](https://github.com/Mohamed-ElGemeie/bookstore-manager-GUI/blob/main/assests/SessionPage.PNG?raw=true)
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

