# Python Gemini API Project

This project demonstrates integration with Google's Gemini API using Python, containerized with Docker for easy deployment and consistency across environments.

## Prerequisites

- Python 3.8+
- Docker
- Google Cloud account with Gemini API access
- Gemini API key

## Project Structure

```
project/
│
├── Dockerfile
├── requirements.tx
├── .gitignore
│── main.py
└── readme.md
```

## Environment Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/project-name.git
cd project-name
```

2. Create a .env file

3. Update the `.env` file with your credentials:
```
geminiAPI=your_api_key_here
```

## Local Development

1. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Docker Setup

1. Build the Docker image:
```bash
docker build -t gemini-project .
```

2. Run the container:
```bash
docker run --env-file .env gemini-project
```

## Docker Environment Variables

The following environment variables can be configured:

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| GEMINI_API_KEY | Your Gemini API authentication key | Yes | - |


## Security Notes

- Never commit your `.env` file to version control
- Add `.env` to your `.gitignore` file
- Regularly rotate your API keys
- Use environment-specific `.env` files for different deployments

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
