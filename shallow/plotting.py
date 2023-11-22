import pandas as pd
import os
import numpy as np
from matplotlib import pyplot as plt

percentage = 10
outer_loop_iterations = 100
cg_iterations = 5

def plot_loss(data_name):

    methods = ["Subsampled", "Method1", "Method2", "Full"]
    os.system(f"mkdir {data_name}_results")    
    plt.xlabel('Time (seconds)')
    plt.ylabel('Function Value')
    plt.yscale('log')
    plt.xscale('log')
    plt.xlim(1e-2, 1e2)
    plt.ylim(1e-5, 1e4)

    plt.title(f"Function Value vs Time (seconds), {percentage}%, \n Outer Loop iterations = {outer_loop_iterations}, max_CG = {cg_iterations}") 

    for method in methods:

        if (method == "Full"):
            os.system(f"(cd Subsampled && make)")
            os.system(f"touch {data_name}_results/{method}_data.txt")
            os.system(f"./Subsampled/train -s 0 -x {outer_loop_iterations} -y {cg_iterations} -z 100 -e 0.00001 {data_name} > {data_name}_results/{method}_data.txt")
        else:
            os.system(f"(cd {method} && make)")
            os.system(f"touch {data_name}_results/{method}_data.txt")
            os.system(f"./{method}/train -s 0 -x {outer_loop_iterations} -y {cg_iterations} -z {percentage} -e 0.00001 {data_name} > {data_name}_results/{method}_data.txt")

        data = pd.read_csv(f"{data_name}_results/{method}_data.txt", sep = " ")

        times = np.array(data["time"])
        function_values = np.array(data["act"])

        plt.plot((times), (function_values))        

    plt.legend(methods)
    plt.show()


plot_loss("news20.binary")