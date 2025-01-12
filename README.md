# Profit Princess - Financial Data Filtering App

**Profit Princess** is a financial data filtering app that allows users to fetch and analyze annual income statements for past stock market data using the Financial Modeling Prep API. The app enables users to filter and sort key financial metrics such as revenue, net income, and earnings per share (EPS), providing valuable insights into the financial performance of the company.

## Features
- Fetch and display annual income statements.
- Filter data by date range, revenue, and net income.
- Sort data by date, revenue, and net income.
- Responsive design for both desktop and mobile devices.

## Technical Stack

Frontend: React TypeScript
Styling: TailwindCSS
Backend : Python with Flask


## AI Policy
Most of my projects use CoPilot, and this is no exception. I do not believe my time is best spent doing simple tasks like creating types for an API call from scratch when we have optimization tools available. What LLMs cannot do: LLM code suggests excessive use of dependencies to do otherwise simple tasks, it is not able to abstract components or organize a file system. While it can create great code comments for easy future maintenance these can often be done either to excess or too brief without human oversight. It absolutely had no idea how to work with a frontend to backend api call using react despite it being quite a basic useFetch function and regularly suggested I filter using the frontend only despite this not being optimal for larger scale data frameworks. These sorts of intricacies require understanding clean code principles and how to create maintainable, not just functional, software. LLMs are a tool, just like a calculator, not a shortcut that will ultimately lead you to being a high level contributor on your development team without a deep understanding of what you aim to create.

## Instructions to Run Locally
### Prerequisites:

  - Node.js installed on your machine.
  - Python installed for the backend.
  - A free API key from Financial Modeling Prep.

### Frontend Setup:

1. Clone the repository:
```
https://github.com/LeeJMorel/ProfitPrincess
```
OR

```
git clone https://github.com/your-username/profit-princess.git
cd profit-princess
```

2. Install the required dependencies:

```
npm install
```

3. Start the React app:

```
npm start
```

4. Change the API to your local port. Under src/api/api.ts change the URL flag.
```
const USE_LOCAL_API = true; 
```

3. Run the developer environment:

```
npm run dev
```

### Backend Setup:

1. Clone the repository:
```
https://github.com/LeeJMorel/ProfitPrincessAPI
```
OR

```
git clone https://github.com/your-username/ProfitPrincessAPI.git
cd ProfitPrincessAPI
```

2. Create a .env file with your API key:

```
API_KEY=your_api_key_here
```

3. Install Python dependencies:

```
pip install -r requirements.txt
```

3. Run the backend locally:

```
python3 api/index.py
```


## License

This project is open source and available under the [MIT License](LICENSE).

