# AlgoScholar

AlgoScholar is an advanced research assistant chatbot powered by the Claude Haiku model. It streamlines academic research workflows by enabling users to quickly search through ARXIV's extensive archive of academic papers in seconds. The project was developed and deployed on AWS SageMaker.

## What is AlgoScholar?

AlgoScholar is a tailored research service designed to help researchers, students, and academics efficiently navigate the vast repository of academic papers available on ARXIV. The application focuses on three key academic domains:

- Computer Science
- Quantitative Finance
- Economics

Users can filter papers by date ranges, engage in natural language conversations about research topics, and receive AI-generated insights about academic literature. The interactive chat interface allows users to ask follow-up questions and explore research topics in depth without having to manually search through numerous papers.

## Features

- **Fast Search**: Instantly search through thousands of ARXIV papers.
- **Summarization**: Generate concise summaries of academic papers.
- **Topic Search**: Find papers on specific topics of interest.
- **Information Retrieval**: Extract detailed information, including authors, references, and abstracts.
- **Network Mapping**: Generate visual network maps of papers and their references.
- **Multiple Chat Sessions**: Maintain up to 5 separate research conversations simultaneously.
- **Response Rating System**: Rate responses for relevance to continuously improve search results.
- **Date Range Filtering**: Filter papers by publication date to focus on recent or specific timeframe research.
- **Interactive Web Interface**: User-friendly Streamlit interface for easy interaction with the AI.

## Development Environment

This project was developed and deployed using **AWS SageMaker**, leveraging its machine learning capabilities and scalable infrastructure for efficient processing of research papers and model training.

## Technical Implementation

### Architecture

AlgoScholar is built with a modern tech stack that enables efficient natural language processing and user interaction:

- **Frontend**: Streamlit web application for interactive user interface
- **Backend**: Python backend for processing requests and managing chat sessions
- **AI Model**: Claude Haiku model for natural language understanding and generation
- **Data Source**: ARXIV papers database organized by academic domains
- **Visualization**: PyVis network for generating visual maps of paper relationships

### Key Components

- **Chat Session Management**: Maintains multiple independent research conversations
- **Document Loading**: Custom document processing pipeline for ARXIV papers
- **Natural Language Processing**: Advanced algorithms for understanding research queries
- **Feedback System**: Continuous improvement through user ratings (1-3 scale)
- **Data Filtering**: Temporal and topic-based filtering of research papers

## Installation

To install AlgoScholar, follow these steps:

1. Clone the repository:
   ```sh
   git clone https://github.com/yourusername/algoscholar.git
   cd algoscholar
   ```

## Initialization

1. Install dependencies:
   ```sh
   pip install --no-cache-dir -r requirements.txt
   ```
2. Setup the environment:
   ```sh
   sh setup.sh
   ```
3. Launch the application:
   ```sh
   sh run.sh
   ```
4. Check status:
   ```sh
   sh status.sh
   ```

## Usage

To run the application:
```sh
sh run.sh
```

To close and clean up resources:
```sh
sh cleanup.sh
```