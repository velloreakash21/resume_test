# Resume Ranking API

The Resume Ranking API is a tool designed to analyze resumes against a set of criteria using OpenAI's language model. It provides scores for each criterion and generates a CSV report of the results.

## Features

- Analyze resumes against custom criteria.
- Generate scores (0-5) for each criterion.
- Produce a CSV report with detailed scoring information.

## Prerequisites

- Python 3.7 or higher
- An OpenAI API key

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/resume_ranking_api.git
   cd resume_ranking_api
   ```

2. Install the required packages:

   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:

   Create a `.env` file in the root directory and add your OpenAI API key:

   ```
   OPENAI_API_KEY=your_openai_api_key
   ```

## Usage

1. Start the server:

   ```bash
   uvicorn resume_ranking_api.main:app --reload
   ```

2. Access the API documentation:

   Open your browser and navigate to [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) to view the Swagger UI.

3. Analyze Resumes:

   Use the `/score-resumes` endpoint to submit resumes and criteria for analysis. The API will return scores for each criterion.

## API Endpoints

- **POST /score-resumes**: Analyze resumes against specified criteria and return scores.

## Example

Here's an example of how to use the API to analyze a resume:

```json
{
  "resumes": [
    {
      "name": "John Doe",
      "text": "John Doe's resume text here..."
    }
  ],
  "criteria": [
    "Proficient with Microsoft Word and Excel",
    "General knowledge of employment law and practices"
  ]
}
```

## Generating Reports

The API can generate a CSV report of the scoring results. The report includes the candidate's name, scores for each criterion, and the total score.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For questions or support, please contact [your email here].
