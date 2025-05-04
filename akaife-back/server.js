const bodyParser = require('body-parser');
const { spawn } = require('child_process');

const express = require('express');
const cors = require('cors');

const app = express();
app.use(cors());

const port = 5000;

app.use(bodyParser.json());

// Route to handle query requests
app.post('/query', (req, res) => {
  const query = req.body.query;
    console.log(
    `Received query: ${query}`
    );
  // Spawn a new Python process to run client.py with the query
  const python = spawn('uv', [
    "run",
    'client.py',
    '/home/nika-rusishvili/Nika/akAIfe/main.py', // Path to your server script
    query, // Pass the query as an argument
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

// Start the server
app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});
