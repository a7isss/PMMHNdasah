'use client';

import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Card,
  CardContent,
  Button,
  Chip,
  Alert,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  TextField,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  CircularProgress,
  Switch,
  FormControlLabel,
} from '@mui/material';
import {
  BugReport,
  Storage,
  Http,
  Assessment,
  ExpandMore,
  PlayArrow,
  Refresh,
  CheckCircle,
  Error,
  Warning,
} from '@mui/icons-material';
import { useAppSelector } from '@/lib/hooks';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`debug-tabpanel-${index}`}
      aria-labelledby={`debug-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

export default function DebugDashboard() {
  const [tabValue, setTabValue] = useState(0);
  const [systemInfo, setSystemInfo] = useState<any>(null);
  const [dbStatus, setDbStatus] = useState<any>(null);
  const [apiTestResults, setApiTestResults] = useState<any[]>([]);
  const [logs, setLogs] = useState<any[]>([]);
  const [metrics, setMetrics] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [testEndpoint, setTestEndpoint] = useState('/api/v1/health');
  const [testMethod, setTestMethod] = useState('GET');
  const [testBody, setTestBody] = useState('');

  const user = useAppSelector((state) => state.auth.user);

  // Check if user is super admin
  if (user?.role !== 'super_admin') {
    return (
      <Container maxWidth="md" sx={{ mt: 4 }}>
        <Alert severity="error">
          Access denied. Super Admin privileges required.
        </Alert>
      </Container>
    );
  }

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const fetchSystemInfo = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/v1/admin/debug/system-info');
      const data = await response.json();
      setSystemInfo(data);
    } catch (error) {
      console.error('Failed to fetch system info:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchDatabaseStatus = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/v1/admin/debug/database-status');
      const data = await response.json();
      setDbStatus(data);
    } catch (error) {
      console.error('Failed to fetch database status:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/v1/admin/debug/logs?limit=50');
      const data = await response.json();
      setLogs(data.logs || []);
    } catch (error) {
      console.error('Failed to fetch logs:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchMetrics = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/v1/admin/debug/metrics');
      const data = await response.json();
      setMetrics(data);
    } catch (error) {
      console.error('Failed to fetch metrics:', error);
    } finally {
      setLoading(false);
    }
  };

  const testApiEndpoint = async () => {
    setLoading(true);
    try {
      const response = await fetch(testEndpoint, {
        method: testMethod,
        headers: {
          'Content-Type': 'application/json',
        },
        body: testMethod !== 'GET' && testBody ? testBody : undefined,
      });
      const data = await response.json();

      const result = {
        timestamp: new Date().toISOString(),
        method: testMethod,
        endpoint: testEndpoint,
        status: response.status,
        statusText: response.statusText,
        response: data,
        success: response.ok,
      };

      setApiTestResults(prev => [result, ...prev.slice(0, 9)]); // Keep last 10 results
    } catch (error: any) {
      const result = {
        timestamp: new Date().toISOString(),
        method: testMethod,
        endpoint: testEndpoint,
        status: 0,
        statusText: 'Network Error',
        response: { error: error.message },
        success: false,
      };
      setApiTestResults(prev => [result, ...prev.slice(0, 9)]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Auto-fetch data when tab changes
    switch (tabValue) {
      case 0:
        fetchSystemInfo();
        break;
      case 1:
        fetchDatabaseStatus();
        break;
      case 3:
        fetchLogs();
        break;
      case 4:
        fetchMetrics();
        break;
    }
  }, [tabValue]);

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
          <BugReport sx={{ mr: 2 }} />
          Debug Dashboard
        </Typography>
        <Typography variant="body1" color="text.secondary">
          System diagnostics, API testing, and debugging tools for administrators
        </Typography>
      </Box>

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={tabValue} onChange={handleTabChange} aria-label="debug tabs">
          <Tab label="System Info" />
          <Tab label="Database" />
          <Tab label="API Testing" />
          <Tab label="Logs" />
          <Tab label="Metrics" />
        </Tabs>
      </Box>

      {/* System Info Tab */}
      <TabPanel value={tabValue} index={0}>
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
              <Typography variant="h6">System Information</Typography>
              <Button
                variant="outlined"
                startIcon={<Refresh />}
                onClick={fetchSystemInfo}
                disabled={loading}
              >
                Refresh
              </Button>
            </Box>

            {systemInfo ? (
              <Box>
                <Accordion defaultExpanded>
                  <AccordionSummary expandIcon={<ExpandMore />}>
                    <Typography variant="h6">Environment Variables</Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <TableContainer component={Paper}>
                      <Table>
                        <TableHead>
                          <TableRow>
                            <TableCell>Variable</TableCell>
                            <TableCell>Value</TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {Object.entries(systemInfo.environment || {}).map(([key, value]: [string, any]) => (
                            <TableRow key={key}>
                              <TableCell component="th" scope="row">{key}</TableCell>
                              <TableCell>{String(value)}</TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </TableContainer>
                  </AccordionDetails>
                </Accordion>

                <Accordion>
                  <AccordionSummary expandIcon={<ExpandMore />}>
                    <Typography variant="h6">Configuration</Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <pre style={{ whiteSpace: 'pre-wrap', fontSize: '12px' }}>
                      {JSON.stringify(systemInfo.config, null, 2)}
                    </pre>
                  </AccordionDetails>
                </Accordion>

                <Accordion>
                  <AccordionSummary expandIcon={<ExpandMore />}>
                    <Typography variant="h6">Runtime Information</Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <pre style={{ whiteSpace: 'pre-wrap', fontSize: '12px' }}>
                      {JSON.stringify(systemInfo.runtime, null, 2)}
                    </pre>
                  </AccordionDetails>
                </Accordion>
              </Box>
            ) : (
              <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
                <CircularProgress />
              </Box>
            )}
          </CardContent>
        </Card>
      </TabPanel>

      {/* Database Tab */}
      <TabPanel value={tabValue} index={1}>
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
              <Typography variant="h6">Database Status</Typography>
              <Button
                variant="outlined"
                startIcon={<Refresh />}
                onClick={fetchDatabaseStatus}
                disabled={loading}
              >
                Refresh
              </Button>
            </Box>

            {dbStatus ? (
              <Box>
                <Box sx={{ mb: 3 }}>
                  <Chip
                    label={dbStatus.status === 'healthy' ? 'Healthy' : 'Issues'}
                    color={dbStatus.status === 'healthy' ? 'success' : 'error'}
                    icon={dbStatus.status === 'healthy' ? <CheckCircle /> : <Error />}
                  />
                </Box>

                <Accordion defaultExpanded>
                  <AccordionSummary expandIcon={<ExpandMore />}>
                    <Typography variant="h6">Connection Details</Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <pre style={{ whiteSpace: 'pre-wrap', fontSize: '12px' }}>
                      {JSON.stringify(dbStatus.connection, null, 2)}
                    </pre>
                  </AccordionDetails>
                </Accordion>

                <Accordion>
                  <AccordionSummary expandIcon={<ExpandMore />}>
                    <Typography variant="h6">Table Statistics</Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <TableContainer component={Paper}>
                      <Table>
                        <TableHead>
                          <TableRow>
                            <TableCell>Table</TableCell>
                            <TableCell align="right">Rows</TableCell>
                            <TableCell align="right">Size (MB)</TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {dbStatus.tables?.map((table: any) => (
                            <TableRow key={table.name}>
                              <TableCell component="th" scope="row">{table.name}</TableCell>
                              <TableCell align="right">{table.row_count}</TableCell>
                              <TableCell align="right">{table.size_mb}</TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </TableContainer>
                  </AccordionDetails>
                </Accordion>
              </Box>
            ) : (
              <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
                <CircularProgress />
              </Box>
            )}
          </CardContent>
        </Card>
      </TabPanel>

      {/* API Testing Tab */}
      <TabPanel value={tabValue} index={2}>
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>API Endpoint Tester</Typography>

            <Box sx={{ display: 'flex', gap: 2, mb: 3, flexWrap: 'wrap' }}>
              <TextField
                label="HTTP Method"
                value={testMethod}
                onChange={(e) => setTestMethod(e.target.value)}
                select
                sx={{ minWidth: 120 }}
              >
                <option value="GET">GET</option>
                <option value="POST">POST</option>
                <option value="PUT">PUT</option>
                <option value="DELETE">DELETE</option>
              </TextField>

              <TextField
                label="Endpoint"
                value={testEndpoint}
                onChange={(e) => setTestEndpoint(e.target.value)}
                sx={{ minWidth: 300, flex: 1 }}
                placeholder="/api/v1/health"
              />

              <Button
                variant="contained"
                startIcon={<PlayArrow />}
                onClick={testApiEndpoint}
                disabled={loading}
              >
                Test
              </Button>
            </Box>

            {testMethod !== 'GET' && (
              <TextField
                label="Request Body (JSON)"
                value={testBody}
                onChange={(e) => setTestBody(e.target.value)}
                multiline
                rows={4}
                fullWidth
                sx={{ mb: 3 }}
                placeholder='{"key": "value"}'
              />
            )}
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>Test Results</Typography>

            {apiTestResults.length === 0 ? (
              <Typography color="text.secondary">No tests run yet</Typography>
            ) : (
              apiTestResults.map((result, index) => (
                <Accordion key={index} sx={{ mb: 1 }}>
                  <AccordionSummary expandIcon={<ExpandMore />}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                      <Chip
                        label={`${result.method} ${result.status}`}
                        color={result.success ? 'success' : 'error'}
                        size="small"
                      />
                      <Typography variant="body2">{result.endpoint}</Typography>
                      <Typography variant="caption" color="text.secondary">
                        {new Date(result.timestamp).toLocaleTimeString()}
                      </Typography>
                    </Box>
                  </AccordionSummary>
                  <AccordionDetails>
                    <pre style={{ whiteSpace: 'pre-wrap', fontSize: '12px', backgroundColor: '#f5f5f5', padding: '8px' }}>
                      {JSON.stringify(result.response, null, 2)}
                    </pre>
                  </AccordionDetails>
                </Accordion>
              ))
            )}
          </CardContent>
        </Card>
      </TabPanel>

      {/* Logs Tab */}
      <TabPanel value={tabValue} index={3}>
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
              <Typography variant="h6">System Logs</Typography>
              <Button
                variant="outlined"
                startIcon={<Refresh />}
                onClick={fetchLogs}
                disabled={loading}
              >
                Refresh
              </Button>
            </Box>

            <TableContainer component={Paper}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Timestamp</TableCell>
                    <TableCell>Level</TableCell>
                    <TableCell>Message</TableCell>
                    <TableCell>Source</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {logs.map((log, index) => (
                    <TableRow key={index}>
                      <TableCell>{new Date(log.timestamp).toLocaleString()}</TableCell>
                      <TableCell>
                        <Chip
                          label={log.level}
                          color={
                            log.level === 'ERROR' ? 'error' :
                            log.level === 'WARNING' ? 'warning' :
                            log.level === 'INFO' ? 'info' : 'default'
                          }
                          size="small"
                        />
                      </TableCell>
                      <TableCell>{log.message}</TableCell>
                      <TableCell>{log.source}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>

            {logs.length === 0 && !loading && (
              <Typography color="text.secondary" sx={{ textAlign: 'center', py: 4 }}>
                No logs available
              </Typography>
            )}
          </CardContent>
        </Card>
      </TabPanel>

      {/* Metrics Tab */}
      <TabPanel value={tabValue} index={4}>
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
              <Typography variant="h6">Performance Metrics</Typography>
              <Button
                variant="outlined"
                startIcon={<Refresh />}
                onClick={fetchMetrics}
                disabled={loading}
              >
                Refresh
              </Button>
            </Box>

            {metrics ? (
              <Box>
                <Accordion defaultExpanded>
                  <AccordionSummary expandIcon={<ExpandMore />}>
                    <Typography variant="h6">System Resources</Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 2 }}>
                      <Card variant="outlined">
                        <CardContent>
                          <Typography variant="h6">CPU Usage</Typography>
                          <Typography variant="h4" color="primary">
                            {metrics.cpu?.usage || 'N/A'}%
                          </Typography>
                        </CardContent>
                      </Card>

                      <Card variant="outlined">
                        <CardContent>
                          <Typography variant="h6">Memory Usage</Typography>
                          <Typography variant="h4" color="secondary">
                            {metrics.memory?.usage || 'N/A'}%
                          </Typography>
                        </CardContent>
                      </Card>

                      <Card variant="outlined">
                        <CardContent>
                          <Typography variant="h6">Active Connections</Typography>
                          <Typography variant="h4" color="success">
                            {metrics.database?.active_connections || 'N/A'}
                          </Typography>
                        </CardContent>
                      </Card>
                    </Box>
                  </AccordionDetails>
                </Accordion>

                <Accordion>
                  <AccordionSummary expandIcon={<ExpandMore />}>
                    <Typography variant="h6">API Performance</Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 2 }}>
                      <Card variant="outlined">
                        <CardContent>
                          <Typography variant="h6">Avg Response Time</Typography>
                          <Typography variant="h4" color="info">
                            {metrics.api?.avg_response_time || 'N/A'}ms
                          </Typography>
                        </CardContent>
                      </Card>

                      <Card variant="outlined">
                        <CardContent>
                          <Typography variant="h6">Requests/Min</Typography>
                          <Typography variant="h4" color="warning">
                            {metrics.api?.requests_per_minute || 'N/A'}
                          </Typography>
                        </CardContent>
                      </Card>

                      <Card variant="outlined">
                        <CardContent>
                          <Typography variant="h6">Error Rate</Typography>
                          <Typography variant="h4" color="error">
                            {metrics.api?.error_rate || 'N/A'}%
                          </Typography>
                        </CardContent>
                      </Card>
                    </Box>
                  </AccordionDetails>
                </Accordion>
              </Box>
            ) : (
              <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
                <CircularProgress />
              </Box>
            )}
          </CardContent>
        </Card>
      </TabPanel>
    </Container>
  );
}
