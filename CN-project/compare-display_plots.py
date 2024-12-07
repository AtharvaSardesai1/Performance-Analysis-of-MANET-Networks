import pandas as pd
import matplotlib.pyplot as plt


data1 = pd.read_csv("dsdv-including_total_time.csv")  
data2 = pd.read_csv("aodv-including_total_time.csv")
data3 = pd.read_csv("dsr-including_total_time.csv")
data4= pd.read_csv("olsr-including_total_time.csv")


plt.figure(figsize=(15, 5))


plt.subplot(1, 4, 1)
plt.plot(data1.index + 1, data1['throughput'], marker='o', color='b', label='dsdv')
plt.plot(data2.index + 1, data2['throughput'], marker='o', color='r', label='aodv')
plt.plot(data3.index + 1, data3['throughput'], marker='o', color='y', label='dsr')
plt.plot(data4.index + 1, data4['throughput'], marker='o', color='m', label='olsr')
plt.title('Throughput Over Runs')
plt.xlabel('Run Number')
plt.ylabel('Throughput')
plt.legend()
plt.grid()


plt.subplot(1, 4, 2)
plt.plot(data1.index + 1, data1['avg_latency'], marker='o', color='b', label='dsdv')
plt.plot(data2.index + 1, data2['avg_latency'], marker='o', color='r', label='aodv')
plt.plot(data3.index + 1, data3['avg_latency'], marker='o', color='y', label='dsr')
plt.plot(data4.index + 1, data4['avg_latency'], marker='o', color='m', label='olsr')
plt.title('Average Latency Over Runs')
plt.xlabel('Run Number')
plt.ylabel('Average Latency (ms)')
plt.legend()
plt.grid()


plt.subplot(1, 4, 3)
plt.plot(data1.index + 1, data1['pdr'], marker='o', color='b', label='dsdv')
plt.plot(data2.index + 1, data2['pdr'], marker='o', color='r', label='aodv')
plt.plot(data3.index + 1, data3['pdr'], marker='o', color='y', label='dsr')
plt.plot(data4.index + 1, data4['pdr'], marker='o', color='m', label='olsr')
plt.title('Packet Delivery Ratio (PDR) Over Runs')
plt.xlabel('Run Number')	
plt.ylabel('PDR (%)')
plt.legend()
plt.grid()

plt.subplot(1, 4, 4)
plt.plot(data1.index + 1, data1['total_time'], marker='o', color='b', label='dsdv')
plt.plot(data2.index + 1, data2['total_time'], marker='o', color='r', label='aodv')
plt.plot(data3.index + 1, data3['total_time'], marker='o', color='y', label='dsr')
plt.plot(data4.index + 1, data4['total_time'], marker='o', color='m', label='olsr')
plt.title('total_time')
plt.xlabel('Run Number')
plt.ylabel('total_time(s)')
plt.legend()
plt.grid()

plt.tight_layout()
plt.show()

