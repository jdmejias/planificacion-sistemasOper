# MLFQ Scheduler Simulator

This project implements a Multilevel Feedback Queue (MLFQ) scheduling simulator using object-oriented programming principles in Python. The simulator is designed to demonstrate the behavior of the MLFQ scheduling algorithm, which is widely used in operating systems to manage process scheduling efficiently.

## Project Structure

```
mlfq-scheduler
├── src
│   ├── main.py          # Entry point of the application
│   ├── scheduler.py     # Contains the MLFQScheduler class
│   ├── process.py       # Contains the Process class
│   └── queue.py         # Contains the Queue class
├── tests
│   ├── test_scheduler.py # Unit tests for MLFQScheduler
│   ├── test_process.py   # Unit tests for Process
│   └── test_queue.py     # Unit tests for Queue
├── requirements.txt      # Project dependencies
└── README.md             # Project documentation
```

## Setup Instructions

1. Clone the repository:
   ```
   git clone <repository-url>
   cd mlfq-scheduler
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

To run the MLFQ scheduler simulator, execute the following command:
```
python src/main.py
```

## Examples

- You can create processes with different burst times and priorities, add them to the scheduler, and observe how the MLFQ algorithm manages their execution based on their priority levels.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.