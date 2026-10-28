# AI Development Notes

## 1. AI Tools Used
I used ChatGPT as a development assistant to understand the requirements, learn the workflow, troubleshoot errors, and prepare documentation.

The application uses Python, Streamlit, Pandas, SQLite, and pytest. It does not currently connect to an external generative AI model.

## 2. How I Used AI During Development
- To understand the project requirements step by step.
- To learn how to run the application and automated tests.
- To interpret test failures and understand the calculations.
- To help publish the source code to GitHub and deploy the dashboard.
- To prepare project documentation.

I checked the suggestions against the application, test results, and dashboard output.

## 3. Problems Encountered
- I was initially unfamiliar with using the terminal and running commands.
- One test failed because the expected month-to-month percentage change was incorrect.
- I needed guidance to configure GitHub and Streamlit deployment.

## 4. How I Debugged Them
- Followed step-by-step instructions to run the application and tests.
- Recalculated the percentage change for the sample data:
  (2200 - 1500) / 1500 * 100 = 46.67%.
- Corrected the test expectation and reran the test suite.
- Verified that seven automated tests passed locally.
- Opened the deployed dashboard and checked the total revenue result of ₹14,39,200.

## 5. What I Would Improve With One More Day
- Support more flexible business questions using an LLM or intent parser.
- Add tests for missing data, invalid dates, and additional edge cases.
- Improve error messages for missing or incorrectly formatted files.
- Add filters for date, product, and region.
- Improve charts and allow users to download filtered results.
- Add automated test execution when code changes are pushed to GitHub.

## 6. Known Limitations
- Question answering uses predefined rules and keywords.
- Only supported question patterns can be answered.
- The application depends on the expected CSV file and column names.
- The current tests cover selected scenarios, not every possible data issue.
- Revenue is calculated from valid completed transactions after data cleaning.
