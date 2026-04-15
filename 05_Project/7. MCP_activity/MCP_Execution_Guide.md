# MCP Campus Helpdesk Starter Code —  Execution Guide

This guide explains **exactly how to run the zip folder step by step** on your computer.

---

## 1. What is inside the zip folder?

After extracting the zip file, you should see a folder similar to this:

```text
mcp_activity_bundle/
├── package.json
├── tsconfig.json
├── README.md
└── src/
    └── server.ts
```

### What these files do
- **package.json** → contains project information, dependencies, and commands.
- **tsconfig.json** → tells TypeScript how to compile the code.
- **src/server.ts** → the main MCP server source code.
- **README.md** → short project overview.

---

## 2. What you need before running it

You need the following installed on your machine:

### Required software
1. **Node.js** version 18 or above
2. **npm** (comes with Node.js)
3. A code editor such as:
   - Visual Studio Code
   - WebStorm
   - Sublime Text
   - Any editor of your choice

### Recommended
- **VS Code Terminal** or normal Command Prompt / PowerShell / Terminal
- An **MCP-compatible client or inspector** for testing later

---

## 3. Check whether Node.js is installed

Open a terminal and run:

```bash
node -v
```

Then run:

```bash
npm -v
```

### Expected result
You should see version numbers, for example:

```bash
v20.18.0
10.8.2
```

### If not installed
Download and install Node.js from the official Node.js website. During installation, keep the default settings.

---

## 4. Extract the zip folder

### On Windows
1. Right-click the zip file.
2. Click **Extract All**.
3. Choose a location such as Desktop.
4. Open the extracted folder.

### On Mac
1. Double-click the zip file.
2. A folder will be created automatically.

### On Linux
Use your file manager or run:

```bash
unzip MCP_Campus_Helpdesk_Starter_Code.zip
```

---

## 5. Open the project folder in a terminal

You must open the terminal **inside the extracted project folder**.

The folder you need is:

```bash
mcp_activity_bundle
```

### Windows Command Prompt example
```bash
cd Desktop\mcp_activity_bundle
```

### Windows PowerShell example
```powershell
cd .\Desktop\mcp_activity_bundle
```

### Mac/Linux example
```bash
cd ~/Desktop/mcp_activity_bundle
```

### Tip
A very easy option is:
- Open the folder in **VS Code**
- Then open **Terminal > New Terminal**

---

## 6. Install the project dependencies

Once you are inside the folder, run:

```bash
npm install
```

### What this does
This downloads all required libraries defined in `package.json`, including:
- `@modelcontextprotocol/sdk`
- `zod`
- `typescript`
- `tsx`

### What you should see
You should see packages being added and no major errors.

Example:

```bash
added 20 packages, and audited 21 packages in 3s
```

### If you get an error
Try:
```bash
npm cache clean --force
npm install
```

---

## 7. Understand the project scripts

Open `package.json` and notice these scripts:

```json
"scripts": {
  "build": "tsc",
  "dev": "tsx src/server.ts",
  "start": "node dist/server.js"
}
```

### Meaning of each command
- **npm run dev** → runs the TypeScript server directly for development
- **npm run build** → compiles TypeScript into JavaScript
- **npm start** → runs the compiled JavaScript version

---

## 8. Run the MCP server in development mode

Use this command:

```bash
npm run dev
```

### Expected output
You should see something like:

```bash
Campus Helpdesk MCP server is running on stdio.
```

This means the server has started successfully.

### Important note
This server runs over **stdio**, so it is designed to talk to an MCP client, not act like a normal website in the browser.

So:
- it will **not** open a webpage
- it will **not** show buttons
- it waits for an MCP-compatible client to communicate with it

---

## 9. What the starter code already does

The current server already contains these tools:

### 1. `list_open_tickets`
Returns helpdesk tickets that are not resolved.

### 2. `create_ticket`
Creates a new support ticket.

### 3. `get_troubleshooting_steps`
Returns troubleshooting steps for issue types like:
- wifi
- lms
- printer
- account

### You task
You must add:
- `update_ticket_status`

Bonus task:
- `tickets_by_priority`

---

## 10. Open and read the main code file

The main file is:

```bash
src/server.ts
```

Open it in your editor.

You will see:
- the MCP server creation
- a sample ticket dataset
- a small troubleshooting knowledge base
- registered MCP tools

---

## 11. How you should edit the code

Inside `src/server.ts`, there is already a comment telling you what to add.

You need to create a new MCP tool named:

```ts
update_ticket_status
```

### It should do the following
1. Accept `ticketId`
2. Accept `status`
3. Validate that status is one of:
   - `open`
   - `in_progress`
   - `resolved`
4. Find the ticket in the array
5. Update the ticket status
6. Return a success message
7. Return a not-found message if the ticket does not exist

---

## 12. Example code you can add

Add this block **below the existing tools** and **above the `main()` function**.

```ts
server.registerTool(
  "update_ticket_status",
  {
    title: "Update Ticket Status",
    description: "Update the status of an existing helpdesk ticket.",
    inputSchema: {
      ticketId: z.string().min(1),
      status: z.enum(["open", "in_progress", "resolved"])
    }
  },
  async ({ ticketId, status }) => {
    const ticket = tickets.find((t) => t.id === ticketId);

    if (!ticket) {
      return {
        content: [
          {
            type: "text",
            text: `Ticket ${ticketId} was not found.`
          }
        ]
      };
    }

    ticket.status = status;

    return {
      content: [
        {
          type: "text",
          text: `Ticket ${ticketId} updated successfully to status: ${status}.`
        }
      ]
    };
  }
);
```

---

## 13. Save the file and run again

After editing the file:

```bash
npm run dev
```

If the code is correct, the server will start normally.

If there is a syntax error, the terminal will show the error line.

---

## 14. How to compile the project

When you finish coding, they should compile the project using:

```bash
npm run build
```

### What this does
This converts TypeScript files from `src/` into JavaScript files in `dist/`.

After building successfully, a `dist` folder will appear.

---

## 15. How to run the compiled version

Run:

```bash
npm start
```

This starts the compiled JavaScript version of the MCP server.

---

## 16. How to test whether the code works

Because this is an MCP server, it should be tested with an MCP-compatible client or inspector.

### Basic testing goals
You should verify that:
1. the server starts without errors
2. `list_open_tickets` works
3. `create_ticket` works
4. `get_troubleshooting_steps` works
5. `update_ticket_status` works after they add it
6. invalid input is handled safely

---

## 17. Suggested manual test cases

### Test Case 1: List current tickets
Expected result:
- the server returns existing tickets such as `T-1001` and `T-1002`

### Test Case 2: Create a new ticket
Input example:
- `studentName`: Sara Ali
- `studentEmail`: sara.ali@example.edu
- `issueType`: wifi
- `priority`: high
- `description`: Cannot connect to Wi-Fi in computer lab.

Expected result:
- a new ticket is created

### Test Case 3: Get troubleshooting steps
Input example:
- `issueType`: lms

Expected result:
- LMS troubleshooting guidance is returned

### Test Case 4: Update ticket status
Input example:
- `ticketId`: T-1001
- `status`: resolved

Expected result:
- the ticket status changes to resolved

### Test Case 5: Invalid ticket
Input example:
- `ticketId`: T-9999
- `status`: resolved

Expected result:
- message says ticket not found

---

## 18. Typical classroom workflow for you:

### Step 1
Extract the zip.

### Step 2
Open terminal in `mcp_activity_bundle`.

### Step 3
Run:

```bash
npm install
```

### Step 4
Open `src/server.ts`.

### Step 5
Read the existing tools.

### Step 6
Add `update_ticket_status`.

### Step 7
Run:

```bash
npm run dev
```

### Step 8
Fix any errors.

### Step 9
Build the project:

```bash
npm run build
```

### Step 10
Run production version:

```bash
npm start
```

### Step 11
Test the server with an MCP client/inspector.

### Step 12
Submit code and screenshots.

---

## 19. Common errors and how to fix them

### Error 1: `node is not recognized`
Cause:
- Node.js is not installed or not added to PATH

Fix:
- Install Node.js again
- Restart the terminal

### Error 2: `npm is not recognized`
Cause:
- npm is missing or PATH is not configured

Fix:
- Reinstall Node.js from the official installer

### Error 3: `Cannot find module`
Cause:
- dependencies not installed

Fix:
Run:

```bash
npm install
```

### Error 4: TypeScript compilation errors
Cause:
- syntax mistake in `server.ts`

Fix:
- check missing commas, brackets, quotes, semicolons
- read the line number shown in terminal

### Error 5: Nothing opens in browser
Cause:
- MCP server is not a normal website

Fix:
- use terminal and an MCP client/inspector to test it

---

## 20. Full command list in order

Here is the full command sequence you will usually use.

### Windows / Mac / Linux
```bash
cd mcp_activity_bundle
npm install
npm run dev
npm run build
npm start
```

---

## 21. Explanation of the existing code structure

### This line creates the MCP server
```ts
const server = new McpServer({
  name: "campus-helpdesk-mcp",
  version: "1.0.0"
});
```

### This line registers a tool
```ts
server.registerTool(...)
```

### This line starts communication over stdio
```ts
const transport = new StdioServerTransport();
await server.connect(transport);
```

That means the MCP server communicates through standard input and output.

---

## 22. What you should submit

A Student should submit:
1. The updated `server.ts` file
2. A screenshot of terminal showing successful run
3. A short explanation of how their `update_ticket_status` tool works
4. Optional: bonus tool implementation
5. Optional: screenshots of successful tests

---

## 23. Bonus task idea

You can add another tool called:

```ts
tickets_by_priority
```

This tool could:
- accept `priority`
- return all tickets matching that priority

Example valid priorities:
- `low`
- `medium`
- `high`

---

## 24. Very short quick-start version

those who want only the minimum steps:

```bash
# 1. Open terminal inside project folder
cd mcp_activity_bundle

# 2. Install dependencies
npm install

# 3. Run development server
npm run dev

# 4. Build the project
npm run build

# 5. Run compiled project
npm start
```

Then edit:

```bash
src/server.ts
```

and add the required `update_ticket_status` tool.

---

## 25. Final note for students

Do not worry if this does not look like a normal web project.
An MCP server is a **backend-style tool server**. Your goal is to:
- understand the MCP pattern
- register tools
- validate inputs
- return useful outputs
- test that your tools work correctly

That is the core learning outcome of this activity.

