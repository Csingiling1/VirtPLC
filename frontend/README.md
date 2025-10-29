# VirtPLC - Industrial Factory Monitoring System

A modern, real-time industrial monitoring and control system built with React, TypeScript, and Vite.

## Project info

**URL**: https://lovable.dev/projects/04908fa3-a1e8-4881-8850-7a894b8bcc4d

## How can I edit this code?

There are several ways of editing your application.

**Use Lovable**

Simply visit the [Lovable Project](https://lovable.dev/projects/04908fa3-a1e8-4881-8850-7a894b8bcc4d) and start prompting.

Changes made via Lovable will be committed automatically to this repo.

**Use your preferred IDE**

If you want to work locally using your own IDE, you can clone this repo and push changes. Pushed changes will also be reflected in Lovable.

The only requirement is having Node.js & npm installed - [install with nvm](https://github.com/nvm-sh/nvm#installing-and-updating)

Follow these steps:

```sh
# Step 1: Clone the repository using the project's Git URL.
git clone <YOUR_GIT_URL>

# Step 2: Navigate to the project directory.
cd <YOUR_PROJECT_NAME>

# Step 3: Install the necessary dependencies.
npm i

# Step 4: Configure environment variables
# The .env file is already included with default settings
# Update VITE_API_BASE_URL in .env if your backend runs on a different URL

# Step 5: Start the development server with auto-reloading and an instant preview.
npm run dev
```

## Backend Requirements

This application requires a backend API server. The backend should provide:

- **Authentication**: POST /auth/login (JWT-based authentication)
- **Data API**: GET /api/data/latest, GET /api/data/range, GET /api/data/health
- **Simulator API**: Full CRUD endpoints for device simulation

Default backend URL: `http://localhost:8080`

To configure a different backend URL, update the `VITE_API_BASE_URL` in the `.env` file.

**Edit a file directly in GitHub**

- Navigate to the desired file(s).
- Click the "Edit" button (pencil icon) at the top right of the file view.
- Make your changes and commit the changes.

**Use GitHub Codespaces**

- Navigate to the main page of your repository.
- Click on the "Code" button (green button) near the top right.
- Select the "Codespaces" tab.
- Click on "New codespace" to launch a new Codespace environment.
- Edit files directly within the Codespace and commit and push your changes once you're done.

## What technologies are used for this project?

This project is built with:

- Vite
- TypeScript
- React
- shadcn-ui
- Tailwind CSS

## How can I deploy this project?

Simply open [Lovable](https://lovable.dev/projects/04908fa3-a1e8-4881-8850-7a894b8bcc4d) and click on Share -> Publish.

## Can I connect a custom domain to my Lovable project?

Yes, you can!

To connect a domain, navigate to Project > Settings > Domains and click Connect Domain.

Read more here: [Setting up a custom domain](https://docs.lovable.dev/features/custom-domain#custom-domain)
