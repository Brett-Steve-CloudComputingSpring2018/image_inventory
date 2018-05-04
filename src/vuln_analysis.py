#!/usr/bin/python

import matplotlib.pyplot as plt
import psycopg2
import operator
import numpy as np

POSTGRES_NAME = 'csci5799'
POSTGRES_USERNAME = 'csciuser'
POSTGRES_PASSWORD = 'csci5799'
POSTGRES_HOST = 'csci5799-postgres.crzz7sianr5s.us-west-2.rds.amazonaws.com'
POSTGRES_PORT = '5432'

def connect():
    
    newConn = psycopg2.connect(dbname=POSTGRES_NAME, user=POSTGRES_USERNAME, password=POSTGRES_PASSWORD, host=POSTGRES_HOST, port=POSTGRES_PORT)

    cursor = newConn.cursor()
    
    return cursor


def count_vulns(plotname):
    
    cursor = connect()
    
    # link to the images database
    
    if plotname == 'httpd':
        cursor.execute("SELECT * FROM images_import WHERE name LIKE 'httpd:%' AND status = 'COMPLETE'")
    elif plotname == 'drupal':
        cursor.execute("SELECT * FROM images_import WHERE name LIKE 'drupal:%' AND status = 'COMPLETE'")
    elif plotname == 'debian':
        cursor.execute("SELECT * FROM images_import WHERE name LIKE 'debian:%' AND status = 'COMPLETE'")
    elif plotname == 'centos':
        cursor.execute("SELECT * FROM images_import WHERE name LIKE 'centos:%' AND status = 'COMPLETE'")
    elif plotname == 'python':
        cursor.execute("SELECT * FROM images_import WHERE name LIKE 'python:%' AND name NOT LIKE '%alpine' AND status = 'COMPLETE'")
    elif plotname == 'official':
        cursor.execute("SELECT * FROM images_import WHERE name NOT LIKE '%/%' AND name NOT LIKE '%:%' AND status = 'COMPLETE'")
    elif plotname == 'public':
        cursor.execute("SELECT * FROM images_import WHERE name LIKE '%/%' AND status = 'COMPLETE'")
    
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
            
    # plot_vuln(total_vulns, "Total")
    # plot_vuln(negligible, "Negligible")
    # plot_vuln(low, "Low")
    # plot_vuln(medium, "Medium")
    # plot_vuln(high, "High")


    plot_vuln((negligible, low, medium, high, total_vulns), plotname)

    # stats((negligible, low, medium, high, total_vulns))


def stats(vuln_dict):

    negligible = vuln_dict[0]
    low = vuln_dict[1]
    medium = vuln_dict[2]
    high = vuln_dict[3]
    total = vuln_dict[4]
    
    print "Official Stats:"
    
    # compute mean
    neg_avg = np.mean(negligible.values())
    low_avg = np.mean(low.values())
    medium_avg = np.mean(medium.values())
    high_avg = np.mean(high.values())
    total_avg = np.mean(total.values())
    print total.values()
    print "Average Negligible Vulnerabilities: " + str(neg_avg)
    print "Average Low Vulnerabilities: " + str(low_avg)
    print "Average Medium Vulnerabilities: " + str(medium_avg)
    print "Average High Vulnerabilities: " + str(high_avg)
    print "Average Total Vulnerabilities: " + str(total_avg)
    
    print "\n"
    # compute variance

    neg_var = np.var(negligible.values())
    low_var = np.var(low.values())
    medium_var = np.var(medium.values())
    high_var = np.var(high.values())
    total_var = np.var(total.values())
    print "Variance of Negligible Vulnerabilities: " + str(neg_var)
    print "Variance of Low Vulnerabilities: " + str(low_var)
    print "Variance of Medium Vulnerabilities: " + str(medium_var)
    print "Variance of High Vulnerabilities: " + str(high_var)
    print "Variance of Total Vulnerabilities: " + str(total_var)
    
    print "\n"
    
    # compute std
    neg_std = np.std(negligible.values())
    low_std = np.std(low.values())
    medium_std = np.std(medium.values())
    high_std = np.std(high.values())
    total_std = np.std(total.values())
    print "Standard Deviation of Negligible Vulnerabilities: " + str(neg_std)
    print "Standard Deviation of Low Vulnerabilities: " + str(low_std)
    print "Standard Deviation of Medium Vulnerabilities: " + str(medium_std)
    print "Standard Deviation of High Vulnerabilities: " + str(high_std)
    print "Standard Deviation of Total Vulnerabilities: " + str(total_std)



def plot_vuln(vuln_dict, fig_name):
    
    
    # sorted_dict = sorted(vuln_dict.items(), key=operator.itemgetter(0))
    
    negligible = vuln_dict[0]
    low = vuln_dict[1]
    medium = vuln_dict[2]
    high = vuln_dict[3]
    total = vuln_dict[4]
    
    sorted_neg = sorted(negligible.items(), key=operator.itemgetter(0))
    sorted_low = sorted(low.items(), key=operator.itemgetter(0))
    sorted_med = sorted(medium.items(), key=operator.itemgetter(0))
    sorted_high = sorted(high.items(), key=operator.itemgetter(0))
    sorted_total = sorted(total.items(), key=operator.itemgetter(0))
    
    fig, ax = plt.subplots(figsize=(10,5))
    
    barWidth = 0.105
    
    xaxis = np.arange(0,len(vuln_dict[0]))
    
    ax.bar(xaxis - barWidth*2 - 0.03, [k[1] for k in sorted_neg], barWidth, color='dodgerblue', label='Negligible')
    ax.bar(xaxis - barWidth - 0.015, [k[1] for k in sorted_low], barWidth, color='seagreen', label='Low')
    ax.bar(xaxis, [k[1] for k in sorted_med], barWidth, color='gold', label='Medium')
    ax.bar(xaxis + barWidth + 0.015, [k[1] for k in sorted_high], barWidth, color='tomato', label='High')
    ax.bar(xaxis + barWidth*2 + 0.03, [k[1] for k in sorted_total], barWidth, color='darkorange', label='Total')
    
    # ax.bar(xaxis - barWidth*2, vuln_dict[0].values(), barWidth, color='Blue', label='Negligible')
    # ax.bar(xaxis - barWidth, vuln_dict[1].values(), barWidth, color='Green', label='Low')
    # ax.bar(xaxis, vuln_dict[2].values(), barWidth, color='Yellow', label='Medium')
    # ax.bar(xaxis + barWidth, vuln_dict[3].values(), barWidth, color='Red', label='High')
    # ax.bar(xaxis + barWidth*2, vuln_dict[4].values(), barWidth, color='Orange', label='Total')
    
    
    ax.yaxis.grid(True)
    # ax.legend(bbox_to_anchor=(1.01, 0.9), loc=2, borderaxespad=0.)
    ax.legend()
    
    
    # plt.bar(range(len(vuln_dict)), vuln_dict.values(), align='center', color='r')
    
    # plt.bar(range(len(vuln_dict)), [k[1] for k in sorted_dict], align='center', color='r')
    
    plt.ylabel("Number of Vulnerabilities")
    plt.xlabel("Docker Image")
    # plt.title("Common Vulnerabilities and Exposures Detected in httpd")
    if fig_name == 'public' or fig_name == 'official':
        plt.xticks(rotation = 90)
    else:
        plt.xticks(rotation = 60)
    # plt.xticks(range(len(vuln_dict[0])), vuln_dict[0].keys())
    plt.xticks(range(len(negligible)), [k[0] for k in sorted_neg])
    plt.tight_layout()
    fig_name += ".png"
    plt.savefig(fig_name)
    plt.clf()
    # plt.show()


if __name__ == '__main__':
    
    # count_vulns('httpd')
    # count_vulns('drupal')
    # count_vulns('debian')
    # count_vulns('centos')
    # count_vulns('python')
    count_vulns('official')
    count_vulns('public')
