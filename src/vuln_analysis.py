

import matplotlib.pyplot as plt
import psycopg2


POSTGRES_NAME = 'csci5799'
POSTGRES_USERNAME = 'csciuser'
POSTGRES_PASSWORD = 'csci5799'
POSTGRES_HOST = 'csci5799-postgres.crzz7sianr5s.us-west-2.rds.amazonaws.com'
POSTGRES_PORT = '5432'

def connect():
    
    newConn = psycopg2.connect(dbname=POSTGRES_NAME, user=POSTGRES_USERNAME, password=POSTGRES_PASSWORD, host=POSTGRES_HOST, port=POSTGRES_PORT)

    cursor = newConn.cursor()
    
    return cursor


def count_vulns():
    
    cursor = connect()
    
    # link to the images database
    cursor.execute("SELECT * FROM images_import")
    
    vuln_cursor = connect()
    
    # store vulnerabilites as key value pairs in dictionary
    # {'image_name':int}
    total_vulns = {}
    
    high = {}
    medium = {}
    low = {}
    negligible = {}
    
    a = 0
    
    for img_row in cursor:
        
        name = img_row[0]
        digest = img_row[4]

        vuln_cursor.execute("SELECT * FROM vulnerabilities WHERE sha256_digest=%s",(digest,))
        
        # each row in the table is a vulnerability so the row count
        # should equal the total number of vulnerabilities for that
        # digest
        count = vuln_cursor.rowcount
        # add that count to the dictionary of values
        total_vulns[name] = count
        
        vuln_cursor.execute("SELECT * FROM vulnerabilities WHERE sha256_digest=%s and severity=%s",(digest,"Negligible"))
        count = vuln_cursor.rowcount
        negligible[name] = count
        
        vuln_cursor.execute("SELECT * FROM vulnerabilities WHERE sha256_digest=%s and severity=%s",(digest,"Low"))
        count = vuln_cursor.rowcount
        low[name] = count
        
        vuln_cursor.execute("SELECT * FROM vulnerabilities WHERE sha256_digest=%s and severity=%s",(digest,"Medium"))
        count = vuln_cursor.rowcount
        medium[name] = count
        
        vuln_cursor.execute("SELECT * FROM vulnerabilities WHERE sha256_digest=%s and severity=%s",(digest,"High"))
        count = vuln_cursor.rowcount
        high[name] = count
        
        
        # right now just look at the first 10 images so our plot isn't unreadable
        a += 1
        if a == 10:
            break
            
    plot_vuln(total_vulns, "Total")
    plot_vuln(negligible, "Negligible")
    plot_vuln(low, "Low")
    plot_vuln(medium, "Medium")
    plot_vuln(high, "High")


def plot_vuln(vuln_dict, fig_name):
    
    
    # TODO - use subplots? make the total vulnerabilities a stacked bar graph?
    
    plt.bar(range(len(vuln_dict)), vuln_dict.values(), align='center', color='r')
    plt.ylabel("Number of " + fig_name + " Vulnerabilities")
    plt.xlabel("Docker Image")
    plt.title("Common Vulnerabilities and Exposures in Containers")
    plt.xticks(rotation = 60)
    plt.xticks(range(len(vuln_dict)), vuln_dict.keys())
    fig_name += ".png"
    plt.savefig(fig_name)
    plt.clf()
    # plt.show()



# def make_plots():
    
    # TODO - make multiple plots plotting stuff for vulnerability analysis
    

if __name__ == '__main__':
    
    count_vulns()
    
