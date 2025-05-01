# Project
 https://docs.google.com/document/d/10UlV9slFx5YdSsMRmowL7-gLAhNFzm-95_gPVgPk6ao/edit?tab=t.0

# Jira Keyword Insight
/Users/trahman/git/freedom/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   └── models/
├── frontend/
│   └── src/
│       ├── components/
│       └── services/
└── requirements.txtfrom fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from .core.config import Settings
from .core.jira_client import JiraClient
from .api import router

app = FastAPI(title="Jira Keyword Insight")

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api")from pydantic import BaseSettings

class Settings(BaseSettings):
    JIRA_API_TOKEN: str
    JIRA_EMAIL: str
    JIRA_URL: str

    class Config:
        env_file = ".env"

settings = Settings()from jira import JIRA
from ..core.config import settings

class JiraClient:
    def __init__(self):
        self.client = JIRA(
            server=settings.JIRA_URL,
            basic_auth=(settings.JIRA_EMAIL, settings.JIRA_API_TOKEN)
        )

    async def search_issues(self, keywords, board_id):
        jql = f'project in (select board {board_id}) AND text ~ "{" OR ".join(keywords)}"'
        issues = self.client.search_issues(jql, maxResults=100)
        return [self._parse_issue(issue) for issue in issues]

    def _parse_issue(self, issue):
        return {
            "key": issue.key,
            "summary": issue.fields.summary,
            "description": issue.fields.description,
            "status": issue.fields.status.name,
            "priority": issue.fields.priority.name if issue.fields.priority else None,
            "assignee": issue.fields.assignee.displayName if issue.fields.assignee else None,
            "type": issue.fields.issuetype.name,
            "url": f"{settings.JIRA_URL}/browse/{issue.key}"
        }from fastapi import APIRouter, HTTPException, Depends
        from ..core.jira_client import JiraClient
        from .schemas import KeywordSearchRequest, KeywordSearchResponse
        
        router = APIRouter()
        jira_client = JiraClient()
        
        @router.post("/search", response_model=KeywordSearchResponse)
        async def search_keywords(request: KeywordSearchRequest):
            try:
                issues = await jira_client.search_issues(request.keywords, request.board_id)
                return KeywordSearchResponse(
                    issues=issues,
                    total_count=len(issues)
                )
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))from pydantic import BaseModel
                from typing import List, Optional
                
                class KeywordSearchRequest(BaseModel):
                    keywords: List[str]
                    board_id: str
                
                class JiraIssue(BaseModel):
                    key: str
                    summary: str
                    description: Optional[str]
                    status: str
                    priority: Optional[str]
                    assignee: Optional[str]
                    type: str
                    url: str
                
                class KeywordSearchResponse(BaseModel):
                    issues: List[JiraIssue]
                    total_count: int{
                      "name": "jira-keyword-insight",
                      "version": "0.1.0",
                      "private": true,
                      "dependencies": {
                        "@emotion/react": "^11.7.0",
                        "@emotion/styled": "^11.6.0",
                        "@mui/material": "^5.2.0",
                        "@mui/icons-material": "^5.2.0",
                        "axios": "^0.24.0",
                        "react": "^17.0.2",
                        "react-dom": "^17.0.2",
                        "react-scripts": "4.0.3"
                      },
                      "scripts": {
                        "start": "react-scripts start",
                        "build": "react-scripts build",
                        "test": "react-scripts test",
                        "eject": "react-scripts eject"
                      },
                      "eslintConfig": {
                        "extends": [
                          "react-app",
                          "react-app/jest"
                        ]
                      },
                      "browserslist": {
                        "production": [
                          ">0.2%",
                          "not dead",
                          "not op_mini all"
                        ],
                        "development": [
                          "last 1 chrome version",
                          "last 1 firefox version",
                          "last 1 safari version"
                        ]
                      }
                    }import axios from 'axios';
                    
                    const API_BASE_URL = 'http://localhost:8000/api';
                    
                    export const searchKeywords = async (keywords, boardId, token) => {
                      const response = await axios.post(`${API_BASE_URL}/search`, {
                        keywords,
                        board_id: boardId
                      }, {
                        headers: {
                          'Authorization': `Bearer ${token}`
                        }
                      });
                      return response.data;
                    };import React, { useState } from 'react';
                    import { 
                      TextField, 
                      Button, 
                      Box, 
                      Paper, 
                      Typography,
                      Chip
                    } from '@mui/material';
                    
                    const SearchForm = ({ onSearch }) => {
                      const [keywords, setKeywords] = useState('');
                      const [boardId, setBoardId] = useState('');
                      const [token, setToken] = useState('');
                    
                      const handleSubmit = (e) => {
                        e.preventDefault();
                        const keywordList = keywords.split(',').map(k => k.trim());
                        onSearch(keywordList, boardId, token);
                      };
                    
                      return (
                        <Paper sx={{ p: 3, mb: 3 }}>
                          <Typography variant="h6" gutterBottom>
                            Search Jira Issues
                          </Typography>
                          <Box component="form" onSubmit={handleSubmit}>
                            <TextField
                              fullWidth
                              label="Jira API Token"
                              type="password"
                              value={token}
                              onChange={(e) => setToken(e.target.value)}
                              margin="normal"
                            />
                            <TextField
                              fullWidth
                              label="Board ID"
                              value={boardId}
                              onChange={(e) => setBoardId(e.target.value)}
                              margin="normal"
                            />
                            <TextField
                              fullWidth
                              label="Keywords (comma-separated)"
                              value={keywords}
                              onChange={(e) => setKeywords(e.target.value)}
                              margin="normal"
                              helperText="Enter keywords separated by commas"
                            />
                            <Button 
                              variant="contained" 
                              type="submit" 
                              sx={{ mt: 2 }}
                              fullWidth
                            >
                              Search
                            </Button>
                          </Box>
                        </Paper>
                      );
                    };
                    
                    export default SearchForm;import React from 'react';
                    import {
                      Paper,
                      Typography,
                      List,
                      ListItem,
                      ListItemText,
                      Chip,
                      Box,
                      Link
                    } from '@mui/material';
                    
                    const ResultsView = ({ results }) => {
                      if (!results || results.length === 0) {
                        return null;
                      }
                    
                      return (
                        <Paper sx={{ p: 3 }}>
                          <Typography variant="h6" gutterBottom>
                            Search Results ({results.length} issues found)
                          </Typography>
                          <List>
                            {results.map((issue) => (
                              <ListItem 
                                key={issue.key}
                                component={Paper}
                                sx={{ mb: 2, p: 2 }}
                              >
                                <ListItemText
                                  primary={
                                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                      <Link href={issue.url} target="_blank" rel="noopener">
                                        {issue.key}
                                      </Link>
                                      <Typography variant="body1">
                                        {issue.summary}
                                      </Typography>
                                    </Box>
                                  }
                                  secondary={
                                    <Box sx={{ mt: 1 }}>
                                      <Chip 
                                        label={issue.status} 
                                        size="small" 
                                        sx={{ mr: 1 }} 
                                      />
                                      <Chip 
                                        label={issue.type} 
                                        size="small" 
                                        sx={{ mr: 1 }} 
                                      />
                                      {issue.priority && (
                                        <Chip 
                                          label={issue.priority} 
                                          size="small" 
                                          sx={{ mr: 1 }} 
                                        />
                                      )}
                                      <Typography variant="body2" sx={{ mt: 1 }}>
                                        {issue.description}
                                      </Typography>
                                    </Box>
                                  }
                                />
                              </ListItem>
                            ))}
                          </List>
                        </Paper>
                      );
                    };
                    
                    export default ResultsView;import React, { useState } from 'react';
                    import { Container, CssBaseline, Typography, Box } from '@mui/material';
                    import SearchForm from './components/SearchForm';
                    import ResultsView from './components/ResultsView';
                    import { searchKeywords } from './services/api';
                    
                    function App() {
                      const [results, setResults] = useState(null);
                      const [error, setError] = useState(null);
                    
                      const handleSearch = async (keywords, boardId, token) => {
                        try {
                          setError(null);
                          const data = await searchKeywords(keywords, boardId, token);
                          setResults(data.issues);
                        } catch (err) {
                          setError(err.message);
                          setResults(null);
                        }
                      };
                    
                      return (
                        <>
                          <CssBaseline />
                          <Container maxWidth="lg">
                            <Box sx={{ my: 4 }}>
                              <Typography variant="h4" component="h1" gutterBottom>
                                Jira Keyword Insight
                              </Typography>
                              <SearchForm onSearch={handleSearch} />
                              {error && (
                                <Typography color="error" sx={{ mb: 2 }}>
                                  Error: {error}
                                </Typography>
                              )}
                              <ResultsView results={results} />
                            </Box>
                          </Container>
                        </>
                      );
                    }
                    
                    export default App;import React from 'react';
                    import ReactDOM from 'react-dom';
                    import App from './App';
                    
                    ReactDOM.render(
                      <React.StrictMode>
                        <App />
                      </React.StrictMode>,
                      document.getElementById('root')
                    );{
                      "name": "jira-keyword-insight",
                      "version": "0.1.0",
                      "private": true,
                      "dependencies": {
                        "@emotion/react": "^11.7.0",
                        "@emotion/styled": "^11.6.0",
                        "@mui/material": "^5.2.0",
                        "@mui/icons-material": "^5.2.0",
                        "axios": "^0.24.0",
                        "react": "^17.0.2",
                        "react-dom": "^17.0.2",
                        "react-scripts": "4.0.3"
                      },
                      "scripts": {
                        "start": "react-scripts start",
                        "build": "react-scripts build",
                        "test": "react-scripts test",
                        "eject": "react-scripts eject"
                      },
                      "eslintConfig": {
                        "extends": [
                          "react-app",
                          "react-app/jest"
                        ]
                      },
                      "browserslist": {
                        "production": [
                          ">0.2%",
                          "not dead",
                          "not op_mini all"
                        ],
                        "development": [
                          "last 1 chrome version",
                          "last 1 firefox version",
                          "last 1 safari version"
                        ]
                      }
                    }import axios from 'axios';
                    
                    const API_BASE_URL = 'http://localhost:8000/api';
                    
                    export const searchKeywords = async (keywords, boardId, token) => {
                      const response = await axios.post(`${API_BASE_URL}/search`, {
                        keywords,
                        board_id: boardId
                      }, {
                        headers: {
                          'Authorization': `Bearer ${token}`
                        }
                      });
                      return response.data;
                    };import React, { useState } from 'react';
                    import { 
                      TextField, 
                      Button, 
                      Box, 
                      Paper, 
                      Typography,
                      Chip
                    } from '@mui/material';
                    
                    const SearchForm = ({ onSearch }) => {
                      const [keywords, setKeywords] = useState('');
                      const [boardId, setBoardId] = useState('');
                      const [token, setToken] = useState('');
                    
                      const handleSubmit = (e) => {
                        e.preventDefault();
                        const keywordList = keywords.split(',').map(k => k.trim());
                        onSearch(keywordList, boardId, token);
                      };
                    
                      return (
                        <Paper sx={{ p: 3, mb: 3 }}>
                          <Typography variant="h6" gutterBottom>
                            Search Jira Issues
                          </Typography>
                          <Box component="form" onSubmit={handleSubmit}>
                            <TextField
                              fullWidth
                              label="Jira API Token"
                              type="password"
                              value={token}
                              onChange={(e) => setToken(e.target.value)}
                              margin="normal"
                            />
                            <TextField
                              fullWidth
                              label="Board ID"
                              value={boardId}
                              onChange={(e) => setBoardId(e.target.value)}
                              margin="normal"
                            />
                            <TextField
                              fullWidth
                              label="Keywords (comma-separated)"
                              value={keywords}
                              onChange={(e) => setKeywords(e.target.value)}
                              margin="normal"
                              helperText="Enter keywords separated by commas"
                            />
                            <Button 
                              variant="contained" 
                              type="submit" 
                              sx={{ mt: 2 }}
                              fullWidth
                            >
                              Search
                            </Button>
                          </Box>
                        </Paper>
                      );
                    };
                    
                    export default SearchForm;import React from 'react';
                    import {
                      Paper,
                      Typography,
                      List,
                      ListItem,
                      ListItemText,
                      Chip,
                      Box,
                      Link
                    } from '@mui/material';
                    
                    const ResultsView = ({ results }) => {
                      if (!results || results.length === 0) {
                        return null;
                      }
                    
                      return (
                        <Paper sx={{ p: 3 }}>
                          <Typography variant="h6" gutterBottom>
                            Search Results ({results.length} issues found)
                          </Typography>
                          <List>
                            {results.map((issue) => (
                              <ListItem 
                                key={issue.key}
                                component={Paper}
                                sx={{ mb: 2, p: 2 }}
                              >
                                <ListItemText
                                  primary={
                                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                      <Link href={issue.url} target="_blank" rel="noopener">
                                        {issue.key}
                                      </Link>
                                      <Typography variant="body1">
                                        {issue.summary}
                                      </Typography>
                                    </Box>
                                  }
                                  secondary={
                                    <Box sx={{ mt: 1 }}>
                                      <Chip 
                                        label={issue.status} 
                                        size="small" 
                                        sx={{ mr: 1 }} 
                                      />
                                      <Chip 
                                        label={issue.type} 
                                        size="small" 
                                        sx={{ mr: 1 }} 
                                      />
                                      {issue.priority && (
                                        <Chip 
                                          label={issue.priority} 
                                          size="small" 
                                          sx={{ mr: 1 }} 
                                        />
                                      )}
                                      <Typography variant="body2" sx={{ mt: 1 }}>
                                        {issue.description}
                                      </Typography>
                                    </Box>
                                  }
                                />
                              </ListItem>
                            ))}
                          </List>
                        </Paper>
                      );
                    };
                    
                    export default ResultsView;import React, { useState } from 'react';
                    import { Container, CssBaseline, Typography, Box } from '@mui/material';
                    import SearchForm from './components/SearchForm';
                    import ResultsView from './components/ResultsView';
                    import { searchKeywords } from './services/api';
                    
                    function App() {
                      const [results, setResults] = useState(null);
                      const [error, setError] = useState(null);
                    
                      const handleSearch = async (keywords, boardId, token) => {
                        try {
                          setError(null);
                          const data = await searchKeywords(keywords, boardId, token);
                          setResults(data.issues);
                        } catch (err) {
                          setError(err.message);
                          setResults(null);
                        }
                      };
                    
                      return (
                        <>
                          <CssBaseline />
                          <Container maxWidth="lg">
                            <Box sx={{ my: 4 }}>
                              <Typography variant="h4" component="h1" gutterBottom>
                                Jira Keyword Insight
                              </Typography>
                              <SearchForm onSearch={handleSearch} />
                              {error && (
                                <Typography color="error" sx={{ mb: 2 }}>
                                  Error: {error}
                                </Typography>
                              )}
                              <ResultsView results={results} />
                            </Box>
                          </Container>
                        </>
                      );
                    }
                    
                    export default App;import React from 'react';
                    import ReactDOM from 'react-dom';
                    import App from './App';
                    
                    ReactDOM.render(
                      <React.StrictMode>
                        <App />
                      </React.StrictMode>,
                      document.getElementById('root')
                    );<!DOCTYPE html>
                    <html lang="en">
                      <head>
                        <meta charset="utf-8" />
                        <meta name="viewport" content="width=device-width, initial-scale=1" />
                        <meta name="theme-color" content="#000000" />
                        <meta name="description" content="Jira Keyword Insight - Search and analyze Jira tickets" />
                        <title>Jira Keyword Insight</title>
                        <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Roboto:300,400,500,700&display=swap" />
                      </head>
                      <body>
                        <noscript>You need to enable JavaScript to run this app.</noscript>
                        <div id="root"></div>
                      </body>
                    </html>JIRA_API_TOKEN=your_api_token_here
                    JIRA_EMAIL=your_email@example.com
                    JIRA_URL=https://your-domain.atlassian.net# This file can be empty, it just marks the directory as a Python packagefrom .routes import router
                    
                    __all__ = ['router']from .config import settings
                    from .jira_client import JiraClient
                    
                    __all__ = ['settings', 'JiraClient']cd backend
                    python -m venv venv
                    source venv/bin/activate  # On Windows: .\venv\Scripts\activate
                    pip install -r requirements.txt
                    cp .env.example .env  # Then edit .env with your Jira credentials
                    uvicorn app.main:app --reloadcd frontend
                    npm install
                    npm start
A tool for QA testers to quickly gain insights from Jira boards by searching for specific keywords and analyzing ticket information.

## Features

- Simple Jira authentication using API tokens
- Keyword-based search across Jira tickets
- Summarized view of relevant test information
- Test coverage suggestions
- Easy navigation to original Jira tickets

## Project Structure

```
jira-keyword-insight/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── api/         # API routes
│   │   ├── core/        # Core functionality
│   │   └── models/      # Data models
├── frontend/            # React frontend
│   ├── src/
│   │   ├── components/  # React components
│   │   └── services/    # API services
└── requirements.txt     # Python dependencies
```

## Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Set up your Jira API token:
```bash
export JIRA_API_TOKEN=your_token_here
export JIRA_EMAIL=your_email@example.com
export JIRA_URL=https://your-domain.atlassian.net
```

3. Start the backend server:
```bash
cd backend
uvicorn app.main:app --reload
```

4. Start the frontend development server:
```bash
cd frontend
npm install
npm start
```

## Configuration

Create a `.env` file in the backend directory with your Jira credentials:

```
JIRA_API_TOKEN=your_token_here
JIRA_EMAIL=your_email@example.com
JIRA_URL=https://your-domain.atlassian.net
```

## Usage

1. Open the web interface at http://localhost:3000
2. Enter your Jira API token
3. Select a Jira board from the dropdown
4. Enter keywords to search for
5. View summarized results and test coverage suggestions

## Security Notes

- Never commit your Jira API token to version control
- Store sensitive credentials in environment variables or secure vaults
- Use HTTPS for all API communications

## Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

MIT License
