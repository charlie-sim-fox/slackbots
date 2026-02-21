# Provisioner

## Objective:
- Provisioner is a Slackbot that collects required details to provision Salesforce access in UAT, Training, and Production. It creates and tracks provisioning requests, posts status updates, and provides Salesforce login instructions plus quick troubleshooting tips.

## Slack channels:
#willowtree-foxone
#foxone-customercare-testing
#foxone-care-development
#foxone-sf-uat
#sierra-dev
#care-sierra
#care-e2e-testing

## Keywords:
UAT account, SF account, Salesforce account, Salesforce development account, Salesforce sandbox account, Sandbox staging account


## Quick Start Guide:
```
:fox_face: FOXOne UAT: Quick Start Guide
:white_check_mark: Prerequisites Before you begin, you must have MFA set up for Okta Preview.

If you haven't used Okta Preview before, contact IT to request MFA setup for your account.
:closed_lock_with_key: Logging In
Go to https://myfox.oktapreview.com/

Click the FOXOne - UAT app tile.
Note: If you see a Salesforce login screen, do not type a username/password. Click the link at the bottom (SSO).
:sos: Troubleshooting

Can't find the App tile? Try the direct link: https://foxone--f1uat.sandbox.my.salesforce.com/
```

## Admin Steps to Perform:
1. Add new user in Okta preview.
2. In 'Title' field add: FOX TESTER.
3. In Okta Admin, add user to 'FOX ONE Care'.
4. Update status with Provisioner Slackbot.

## User Flow:
1. User initiates by asking for UAT account in slack channels when a keyword is used.
2. Slackbot confirms with user that they want to request a UAT account or report when they have an issue with UAT account.
3. Slackbot asks user to provide required fields: First name, Last name, email.
4. Slack bot collects information, generates a tracking ID (random alpha-numeric 7 character ID) and sends information to #care_tools channel.
5. Slackbot sends confirmation that request was submitted and the status is 'In Progress'.
6. In #care_tools channel, the posted information allows the admin to click a button to update status and allow admin to select status 'Complete' or 'Blocked'. when button is clicked, it should post a message in the original slack channel the request originated from and created a threaded message with status: "Your request is <status>." Status will either be Complete or Blocked. If the status is Complete, it should also provide the quick start guide.
7. Slackbot needs slash command: /provisioner-help that providees the Quick Start Guide and a button that allows user to start the UAT account request process.
8. When Slackbot sends request to #care_tools channel, along with the requested information and tracking ID, it should also provide the steps for the admin to perform. 

