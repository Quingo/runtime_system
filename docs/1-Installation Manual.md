# Installation Manual

Note: Although Quingo is developed with cross-platform in mind, related toolchain for Quingo has been mostly tested under Windows OS.
<!-- It is recommended to use Quingo in a Windows environment. You can start your quantum programming with either a Quingo runtime system or a Quingo plugin. -->

 ## Develop with Runtime System
 To develop a Quingo project with runtime system, a Quingo development kit is required. The Quingo development kit consists of :

 - Quingo runtime system development kit `qgrtsys`
 - Quantum circuit simulator [QuantumSim](https://gitlab.com/quantumsim/quantumsim)

 ### Dependencies

 - [Python(3.7.x)](https://www.python.org/downloads/release/python-377/)：Please do not install python through Anaconda and install python through the official website. If python has already be installed through Anaconda, please uninstall it.
 - [JDK8](https://www.oracle.com/java/technologies/javase/javase-jdk8-downloads.html)

 ## Quingo Runtime System Development Kit

 Quingo runtime system development kit `qgrtsys` consists of runtime system, Quingo compiler, a quantum control architecture simulator `Cactus` and a quantum computing simulator `QuantumSim `( `QuantumSim ` is a GPU-accelerated full density matrix simulator of quantum circuits and is optional for Quingo simulation.) The runtime system development kit `qgrtsys` can realize the data interaction of kernel, host, and compiler. It can also call compiler to compile your Quingo program and call `Cactus` to verify your project. You can get `qgrtsys` from [Quingo repository](https://git.pcl.ac.cn/CQC-QCA/Quingo/src/branch/hotfix_organize_dir) 

 To set up `qgrtsys`, enter the root directory of Quingo, and execute the following command:

 ```
 python setup.py develop
 ```

 or

 ```
 pip install -e .
 ```

 To verify the installation, execute the following command:

 ```
 pip show qgrtsys
 ```

 To verify the installation of quantum simulator, execute the following command:

 ```
 pip show quantumsim
 ```



 ## Develop with Quingo plugin
 Quingo plugin can help you developing Quingo project using VS Code. It should be noted that using Quingo plugin you can only compile your project and generate eQASM file, if you want to check the results, please use `Cactus` and `Quantumsim` to execute your eQASM file.

 ### Dependencies
 - [Visual Studio Code](https://code.visualstudio.com/)

 ### Quingo Plugin
 Quingo plugin is a VS Code plugin that can used to help you write and compile your Quingo project. The latest version of Quingo plugin can be found in [website](https://git.pcl.ac.cn/CQC-QCA/Quingo_plugin/src/branch/master).

 To setup Quingo plugin, download `vsix` plugin file in the above website, then follow these steps to install it in VS Code::
 1. Open VS Code and select `Extensions` in sidebar(or press `Ctrl + Shift + X`).
 2. In `Extensions` bar, click `More actions...` button and select `install from VSIX...`.
 3. Select the Quingo plugin file in the pop-up window.
 4. If the installation is completed, you can find Quingo plugin in your installed extensions.


 Now start your first Quingo project!