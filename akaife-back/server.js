const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const { spawn } = require('child_process');
const path = require('path');

const app = express();
const port = 5000;

// Middleware
app.use(cors());
app.use(bodyParser.json());

// Route to handle query requests
app.post('/query', (req, res) => {
  const query = req.body.query;
  console.log(`Received query: ${query}`);
  
  // Use absolute paths for better reliability
  const clientPath = path.join(__dirname, 'client.py');
  const mainPath = path.join(__dirname, '..', 'main.py');
  
  // Spawn a new Python process to run client.py with the query
  const python = spawn('uv', [
    'run',
    clientPath,
    mainPath,
    query
  ]);

  let response = '';

  // Collect the output from the Python process
  python.stdout.on('data', (data) => {
    response += data.toString();
  });

  python.stderr.on('data', (data) => {
    console.error(`stderr: ${data}`);
  });

  python.on('close', (code) => {
    if (code === 0) {
      res.json({ response });
    } else {
      res.status(500).json({ error: 'Python script failed' });
    }
  });
});

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'OK', message: 'Travel advisor server is running' });
});

// Start the server
app.listen(port, () => {
  console.log(`🚀 Travel Advisor Server running at http://localhost:${port}`);
});
