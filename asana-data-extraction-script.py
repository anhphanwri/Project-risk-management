import csv 
import asana
from asana.rest import ApiException
from datetime import datetime

# Set up Asana API configuration
configuration = asana.Configuration()
configuration.access_token = ‘##########’
api_client = asana.ApiClient(configuration)

# Create instances of the API classes
portfolios_api_instance = asana.PortfoliosApi(api_client)
projects_api_instance = asana.ProjectsApi(api_client)
sections_api_instance = asana.SectionsApi(api_client)
tasks_api_instance = asana.TasksApi(api_client)

portfolio_gid = "1207290077447507"  # Globally unique identifier for the portfolio.
opts = {'opt_fields': 'name,gid,custom_fields.name,custom_fields.display_value,created_at,modified_at'}

try:
    # Get portfolio name
    portfolio_info = portfolios_api_instance.get_portfolio(portfolio_gid, opts)
    portfolio_name = portfolio_info['name']
    portfolio_id = portfolio_info['gid']

    # Define the filename for the consolidated CSV file
    filename = "project_risk_management_dashboard_real_data.csv"
    # Open the consolidated CSV file in write mode
    with open(filename, mode='w', newline='') as consolidated_file:
        writer = csv.writer(consolidated_file)
        # Write the header row
        writer.writerow(["Portfolio Name", "Portfolio ID", "Project Name", "Project ID", "Risk Name", "Risk ID", 
                         "Link to the risk", "Data Extraction Date", "Task Creation Date", "Last Modified Date", "WRI Program", "Office", "Project Life Cycle Phase", "Risk Impact Category", "Risk Likelihood", 
                         "Risk Impact Level", "Risk Assessment", "Risk Strategy", "Risk Management Action", 
                         "Risk Budget", "Risk Status", "Risk Owner", "Close Out Date"]) 

        # Get portfolio items
        portfolio_items = portfolios_api_instance.get_items_for_portfolio(portfolio_gid, opts)

        for project in portfolio_items:
            project_gid = project['gid']
            project_name = project['name']

            # Get the project's sections
            sections_response = sections_api_instance.get_sections_for_project(project_gid, opts)

            # Find the sections named "ACTIVE RISKS" or "INACTIVE RISKS" and get the IDs
            active_risks_section_id = None
            for section in sections_response:
                if section["name"] == "ACTIVE RISKS" or section["name"] == "INACTIVE RISKS":
                    risks_section_id = section["gid"]
                    break

            if risks_section_id:
                # Get tasks from the "ACTIVE RISKS" and "INACTIVE RISKS" sections
                api_response = tasks_api_instance.get_tasks_for_section(risks_section_id, opts)

                # Iterate over tasks
                for task in api_response:
                    # Extract task name
                    task_name = task['name']
                    # Extract gid of each task
                    gid = task.get('gid', [])
                    # Construct task link
                    task_link = f"https://app.asana.com/0/{project_gid}/{gid}"
                    # Extract custom fields
                    custom_fields = task.get('custom_fields', [])
                    # Extract created time
                    created_time = task.get('created_at', "")
                    # Extract last modified time
                    last_modified = task.get('modified_at', "")
                    # Initialize a list to store field values for the current task
                    row_data = [portfolio_name, portfolio_id, project_name, project_gid, task_name, gid, task_link, 
                                datetime.now().strftime("%Y-%m-%d %H:%M:%S"), created_time, last_modified]
                    # Assign values to custom fields if available
                    for field_name in ["WRI Program", "Office", "Project Life Cycle Phase ", "Risk Impact Category", "Risk Likelihood",
                                       "Risk Impact Level", "Risk Assessment", "Risk Strategy",
                                       "Risk Management Action", "Risk Budget (USD)", "Risk Status",
                                       "Risk Owner", "Close Out Date"]:
                        field_value = next(
                                (field['display_value'] for field in custom_fields if field['name'] == field_name),
                                "")
                        row_data.append(field_value)

                    # Write the row to the consolidated CSV file
                    writer.writerow(row_data)

    print(f"Output saved to '{filename}'")

except ApiException as e:
    print("Exception occurred: %s\n" % e)
