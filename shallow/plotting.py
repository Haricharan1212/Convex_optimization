import pandas as pd
import os
import numpy as np
from matplotlib import pyplot as plt

percentage = 20
outer_loop_iterations = 100
cg_iterations = 5

def plot_loss(data_name, tolerance):

    methods = ["Method2", "Method2-g"]
    os.system(f"mkdir {data_name}_results")    

    plt.title(f"Error vs Time (seconds) for {data_name}, {100/percentage}%, \n Outer Loop iterations = {outer_loop_iterations}, max_CG = {cg_iterations}") 
    # plt.title(f"Error vs Number of iterations for {data_name}, {percentage}%, \n Outer Loop iterations = {outer_loop_iterations}, max_CG = {cg_iterations}") 

    # fig = plt.figure()
    # ax = plt.axes(projection='3d')
    # plt.title(f"Error vs Number of iterations vs Time for {data_name}, {percentage}%, \n Outer Loop iterations = {outer_loop_iterations}, max_CG = {cg_iterations}") 

    for method in methods:
        if (method == "Full"):
            os.system(f"(cd Subsampled && make)")
            os.system(f"touch {data_name}_results/{method}_data.txt")
            os.system(f"./Subsampled/train -s 0 -x {outer_loop_iterations} -y {cg_iterations} -z 1 -e {tolerance} {data_name} > {data_name}_results/{method}_data.txt")
        else:
            os.system(f"(cd {method} && make)")
            os.system(f"touch {data_name}_results/{method}_data.txt")
            os.system(f"./{method}/train -s 0 -x {outer_loop_iterations} -y {cg_iterations} -z {percentage} -e {tolerance} {data_name} > {data_name}_results/{method}_data.txt")

        data = pd.read_csv(f"{data_name}_results/{method}_data.txt", sep = " ", skipinitialspace = True)

        num_iterations = np.array(data["iter"])
        times = np.array(data["time"])
        function_values = np.array(data["act"])
    
        plt.plot((times), (function_values), marker = '.') 
        # plt.plot(num_iterations, function_values)        

        # ax.plot3D(times, num_iterations, function_values)

    methods = ["Our paper (S3)", "Our improvements (S4)"]

    # ax.set_xlabel('Time (in seconds)')
    # ax.set_ylabel('Number of Iterations')
    # ax.set_zlabel("Error Value")
    # ax.set_zscale('log')

    plt.xlabel('Time (seconds)')
    plt.ylabel('Error Value')
    plt.yscale('log')
    plt.xscale('log')

    # plt.xlabel('Number of Iterations')
    # plt.ylabel('Error Value')
    # plt.yscale('log')

    plt.legend(methods)
    plt.show()

def plots_2(data_name, tolerance):

    plt.title(f"Convergence & max_CG: Error vs Time (seconds) for {data_name} \n {100/percentage}%, Outer Loop iterations = {outer_loop_iterations}") 

    method = "Method2"

    cg_values = [5, 10, 50, 100]

    for cg_iterations in cg_values:

        os.system(f"(cd {method} && make)")
        os.system(f"touch {data_name}_results/{method}_data.txt")
        os.system(f"./{method}/train -s 0 -x {outer_loop_iterations} -y {cg_iterations} -z {percentage} -e {tolerance} {data_name} > {data_name}_results/{method}_data.txt")

        data = pd.read_csv(f"{data_name}_results/{method}_data.txt", sep = " ", skipinitialspace = True)

        num_iterations = np.array(data["iter"])
        times = np.array(data["time"])
        function_values = np.array(data["act"])

        plt.plot((times), (function_values), marker = '.') 

    plt.xlabel('Time (seconds)')
    plt.ylabel('Error Value')
    plt.yscale('log')
    plt.xscale('log')

    plt.legend([f"max_CG = {i}" for i in cg_values])
    plt.show()


# plots_2("news20.binary", 1e-5)    
plot_loss("phishing", 1e-5)
# plot_loss("kdda", 1e-1)
