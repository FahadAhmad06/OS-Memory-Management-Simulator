# 🖥️ OS Memory Management Simulator

<p align="center">
  <strong>A GUI-Based Operating Systems Group Project</strong>
  <br>
  Exploring Memory Allocation, Paging, Address Translation & Page Replacement
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Project-Operating%20Systems-blue?style=for-the-badge">
  <img src="https://img.shields.io/badge/Type-Group%20Project-purple?style=for-the-badge">
  <img src="https://img.shields.io/badge/Status-In%20Development-orange?style=for-the-badge">
</p>

---

## 📖 About The Project

**OS Memory Management Simulator** is a collaborative university group project developed as part of the Operating Systems course.

The project focuses on understanding and visualizing fundamental memory management concepts used by modern operating systems. It provides a graphical environment where users can explore different memory allocation strategies, understand paging and address translation, and simulate various page replacement algorithms.

Through interactive simulations and visual representations, the application aims to make complex operating system concepts easier to understand and analyze.

## ✨ Features

- 🎨 Interactive and user-friendly Graphical User Interface (GUI).
- 🧠 Multiple contiguous memory allocation strategies.
- 📦 Visual representation of memory blocks and allocation.
- 🔄 Paging and logical-to-physical address translation.
- 📊 Interactive page replacement simulations.
- 📈 Page fault counting and performance analysis.
- ⚡ Comparison of different memory management algorithms.
- 🎯 Step-by-step visualization of algorithm execution.

## 🧩 Project Modules

### 1. Contiguous Memory Allocation

This module demonstrates how an operating system allocates memory to processes using different allocation strategies.

| Algorithm | Description |
|---|---|
| **First Fit** | Allocates the first available memory block that is large enough. |
| **Best Fit** | Allocates the smallest available block that can accommodate the process. |
| **Worst Fit** | Allocates the largest available memory block. |

**Planned functionality:**
- Input memory block sizes.
- Input process sizes.
- Visualize memory allocation.
- Display allocated and unallocated processes.
- Show remaining memory in each block.

### 2. Paging & Address Translation

This module demonstrates paging, where logical memory is divided into pages and physical memory is divided into frames.

**Planned functionality:**
- Logical address input.
- Page number calculation.
- Offset calculation.
- Page table visualization.
- Logical-to-physical address translation.
- Display translated physical addresses.

### 3. Page Replacement Algorithms

This module demonstrates how an operating system manages pages when available physical memory frames are full.

| Algorithm | Description |
|---|---|
| **FIFO** | Replaces the page that entered memory first. |
| **LRU** | Replaces the least recently used page. |
| **Optimal** | Replaces the page that will not be needed for the longest time in the future. |

**Planned functionality:**
- Page reference string input.
- Frame allocation visualization.
- Step-by-step page replacement.
- Page hit and page fault detection.
- Total page fault calculation.
- Algorithm performance comparison.

## 🎨 Graphical User Interface

The project will include a graphical interface designed to provide an interactive learning experience.

**Planned GUI sections:**

- Main Dashboard
- Memory Allocation Simulator
- Paging Simulator
- Address Translation
- Page Replacement Simulator
- Algorithm Comparison
- Results and Statistics

The GUI will allow users to provide inputs, execute simulations, and observe how each algorithm manages memory.

## 🗂️ Project Structure

The following is the proposed directory structure for organizing the project modules.

```text
OS-Memory-Management-Simulator/
│
├── README.md
│
├── src/
│   ├── allocation/
│   │   ├── first_fit.cpp
│   │   ├── best_fit.cpp
│   │   └── worst_fit.cpp
│   │
│   ├── paging/
│   │   └── address_translation.cpp
│   │
│   ├── page_replacement/
│   │   ├── fifo.cpp
│   │   ├── lru.cpp
│   │   └── optimal.cpp
│   │
│   └── gui/
│
├── screenshots/
│
├── docs/
│
└── .gitignore
```

*Note: This is a suggested structure. Actual folders and files may vary depending on the implementation and GUI framework.*

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Programming Language | Core algorithm implementation |
| GUI Framework | Graphical user interface |
| Git | Version control |
| GitHub | Team collaboration and source code management |

*The exact technologies will be documented once finalized.*

## 🚀 Getting Started

Follow these steps to download the project and run it on your local machine.

### Prerequisites

Before running the project, make sure you have:

- Git installed.
- The required programming language installed.
- A suitable code editor or IDE.
- Required GUI framework and dependencies.

### 1. Clone the Repository

Open your terminal or CMD and execute:

```bash
git clone https://github.com/FahadAhmad06/OS-Memory-Management-Simulator.git
```

### 2. Navigate to the Project Directory

```bash
cd OS-Memory-Management-Simulator
```

### 3. Open in VS Code

```bash
code .
```

### 4. Install Dependencies

Install the required dependencies according to the selected programming language and GUI framework.

### 5. Run the Application

Execute the main application file using the appropriate compiler or runtime.

*Detailed installation and execution commands will be added after the development environment is finalized.*

## 📸 Screenshots & Preview

Screenshots of the application and its simulations will be added as development progresses.

| Module | Preview |
|---|---|
| Main Dashboard | Coming Soon |
| Memory Allocation | Coming Soon |
| Paging & Address Translation | Coming Soon |
| Page Replacement | Coming Soon |
| Algorithm Comparison | Coming Soon |

## 📊 Performance Analysis

The simulator aims to provide a practical comparison of the implemented algorithms.

**Memory Allocation Analysis**
- Memory block utilization.
- Process allocation results.
- Remaining memory.
- Allocation success and failure.

**Page Replacement Analysis**
- Total page faults.
- Total page hits.
- Page fault ratio.
- Performance comparison between FIFO, LRU, and Optimal.

## 👥 Project Team

This project is collaboratively developed by our group as part of the Operating Systems coursework.

| No. | Team Member | GitHub Profile |
|---|---|---|
| 1 | Fahad Ahmad | [@FahadAhmad06](https://github.com/FahadAhmad06) |
| 2 | Muhammad Afnan | [@muhammadAfnan2005](https://github.com/muhammadAfnan2005) |
| 3 | Subhan Khan | Add GitHub Profile |

## 🤝 Team Collaboration

We use GitHub to manage the project and coordinate development among group members.

- Each member works on assigned project modules.
- Separate branches are used for individual contributions.
- Pull requests are used to review and merge changes.
- The main branch maintains the integrated project code.

## 🎯 Project Objectives

- Understand operating system memory management.
- Explore contiguous memory allocation techniques.
- Learn paging and address translation.
- Understand different page replacement strategies.
- Visualize how memory is allocated and managed.
- Analyze and compare algorithm performance.
- Apply theoretical Operating Systems concepts through practical implementation.

## 🔮 Future Enhancements

- Improved interactive memory visualization.
- Step-by-step algorithm execution controls.
- Advanced performance comparison charts.
- Enhanced GUI design and user experience.
- Additional memory management techniques.

## 🎓 Academic Information

| Detail | Information |
|---|---|
| Institution | University of Veterinary and Animal Sciences (UVAS), Lahore |
| Course | Operating Systems |
| Project Title | OS Memory Management Simulator |
| Project Type | Group Project |
| Domain | Operating Systems / Memory Management |

## 📄 License

This project is developed for educational and academic purposes as part of our university coursework.

---

<p align="center">
  <strong>OS Memory Management Simulator</strong>
  <br>
  Developed with teamwork, learning, and collaboration. 💻
  <br><br>
  ⭐ If you find this project interesting, consider giving the repository a star!
</p>
