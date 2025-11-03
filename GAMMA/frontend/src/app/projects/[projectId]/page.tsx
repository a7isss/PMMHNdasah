'use client';

import React from 'react';
import { useParams, useRouter } from 'next/navigation';
import {
  Box,
  Typography,
  Paper,
  Card,
  CardContent,
  Button,
  Chip,
  Avatar,
  AvatarGroup,
  LinearProgress,
  Tabs,
  Tab,
  Breadcrumbs,
  Link as MuiLink,
} from '@mui/material';
import {
  Assignment,
  People,
  Timeline,
  ShoppingCart,
  WhatsApp,
  Dashboard,
  Task,
  Assessment,
  ArrowBack,
} from '@mui/icons-material';
import Link from 'next/link';
import { useGetProjectQuery } from '@/lib/api/projectsApi';
import { useGetProjectTasksQuery } from '@/lib/api/tasksApi';
import { useGetUsersQuery } from '@/lib/api/usersApi';

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
      id={`project-tabpanel-${index}`}
      aria-labelledby={`project-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

export default function ProjectDetailPage() {
  const params = useParams();
  const router = useRouter();
  const projectId = params.projectId as string;

  const [tabValue, setTabValue] = React.useState(0);

  const { data: projectData, isLoading: projectLoading } = useGetProjectQuery(projectId);
  const { data: tasksData } = useGetProjectTasksQuery(projectId);
  const { data: usersData } = useGetUsersQuery({});

  const project = projectData?.data;
  const tasks = tasksData?.data || [];
  const users = usersData?.data || [];

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  if (projectLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 400 }}>
        <Typography>Loading project...</Typography>
      </Box>
    );
  }

  if (!project) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography variant="h6" color="error">
          Project not found
        </Typography>
        <Button startIcon={<ArrowBack />} onClick={() => router.back()} sx={{ mt: 2 }}>
          Go Back
        </Button>
      </Box>
    );
  }

  const completedTasks = tasks.filter((task: any) => task.status === 'completed').length;
  const inProgressTasks = tasks.filter((task: any) => task.status === 'in_progress').length;
  const totalTasks = tasks.length;
  const avgProgress = totalTasks > 0
    ? Math.round(tasks.reduce((sum: number, task: any) => sum + (task.progress_percentage || 0), 0) / totalTasks)
    : 0;

  return (
    <Box sx={{ p: 3 }}>
      {/* Breadcrumbs */}
      <Breadcrumbs sx={{ mb: 2 }}>
        <MuiLink component={Link} href="/" underline="hover">
          Dashboard
        </MuiLink>
        <Typography color="text.primary">{project.name}</Typography>
      </Breadcrumbs>

      {/* Project Header */}
      <Box sx={{ mb: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
          <Box>
            <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 1 }}>
              {project.name}
            </Typography>
            <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
              {project.description}
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
              <Chip
                label={project.status}
                color={project.status === 'active' ? 'success' : 'default'}
                size="small"
              />
              <Typography variant="body2" color="text.secondary">
                Created {new Date(project.created_at).toLocaleDateString()}
              </Typography>
            </Box>
          </Box>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Button
              variant="outlined"
              startIcon={<Task />}
              component={Link}
              href={`/projects/${projectId}/tasks`}
            >
              Manage Tasks
            </Button>
            <Button
              variant="outlined"
              startIcon={<ShoppingCart />}
              component={Link}
              href={`/projects/${projectId}/procurement`}
            >
              Procurement
            </Button>
            <Button
              variant="outlined"
              startIcon={<WhatsApp />}
              component={Link}
              href="/whatsapp"
            >
              WhatsApp
            </Button>
          </Box>
        </Box>
      </Box>

      {/* Project Stats */}
      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 3, mb: 3 }}>
        <Card sx={{ flex: '1 1 200px' }}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <Assignment sx={{ mr: 1, color: 'primary.main' }} />
              <Typography variant="h6">{totalTasks}</Typography>
            </Box>
            <Typography variant="body2" color="text.secondary">
              Total Tasks
            </Typography>
          </CardContent>
        </Card>
        <Card sx={{ flex: '1 1 200px' }}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <Timeline sx={{ mr: 1, color: 'success.main' }} />
              <Typography variant="h6">{completedTasks}</Typography>
            </Box>
            <Typography variant="body2" color="text.secondary">
              Completed
            </Typography>
          </CardContent>
        </Card>
        <Card sx={{ flex: '1 1 200px' }}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <Assessment sx={{ mr: 1, color: 'warning.main' }} />
              <Typography variant="h6">{inProgressTasks}</Typography>
            </Box>
            <Typography variant="body2" color="text.secondary">
              In Progress
            </Typography>
          </CardContent>
        </Card>
        <Card sx={{ flex: '1 1 200px' }}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <Dashboard sx={{ mr: 1, color: 'info.main' }} />
              <Typography variant="h6">{avgProgress}%</Typography>
            </Box>
            <Typography variant="body2" color="text.secondary">
              Avg Progress
            </Typography>
          </CardContent>
        </Card>
      </Box>

      {/* Progress Overview */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 2, fontWeight: 'bold' }}>
            Project Progress
          </Typography>
          <Box sx={{ mb: 1 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
              <Typography variant="body2">Overall Completion</Typography>
              <Typography variant="body2">{avgProgress}%</Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={avgProgress}
              sx={{ height: 8, borderRadius: 4 }}
            />
          </Box>
        </CardContent>
      </Card>

      {/* Tabs for different views */}
      <Paper sx={{ width: '100%' }}>
        <Tabs
          value={tabValue}
          onChange={handleTabChange}
          indicatorColor="primary"
          textColor="primary"
          variant="fullWidth"
        >
          <Tab label="Overview" />
          <Tab label="Tasks" />
          <Tab label="Team" />
          <Tab label="Procurement" />
        </Tabs>

        <TabPanel value={tabValue} index={0}>
          <Typography variant="h6" sx={{ mb: 2 }}>Project Overview</Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 3 }}>
            <Card sx={{ flex: '1 1 400px' }}>
              <CardContent>
                <Typography variant="h6" sx={{ mb: 2 }}>Project Details</Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="body2" color="text.secondary">Budget:</Typography>
                    <Typography variant="body2">${project.budget_total?.toLocaleString() || 'Not set'}</Typography>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="body2" color="text.secondary">Status:</Typography>
                    <Chip label={project.status} size="small" />
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="body2" color="text.secondary">Created:</Typography>
                    <Typography variant="body2">{new Date(project.created_at).toLocaleDateString()}</Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
            <Card sx={{ flex: '1 1 400px' }}>
              <CardContent>
                <Typography variant="h6" sx={{ mb: 2 }}>Quick Actions</Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                  <Button
                    variant="outlined"
                    startIcon={<Task />}
                    component={Link}
                    href={`/projects/${projectId}/tasks`}
                    fullWidth
                  >
                    Manage Tasks
                  </Button>
                  <Button
                    variant="outlined"
                    startIcon={<ShoppingCart />}
                    component={Link}
                    href={`/projects/${projectId}/procurement`}
                    fullWidth
                  >
                    Procurement Requests
                  </Button>
                  <Button
                    variant="outlined"
                    startIcon={<People />}
                    component={Link}
                    href={`/projects/${projectId}/team`}
                    fullWidth
                  >
                    Manage Team
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Box>
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <Typography variant="h6" sx={{ mb: 2 }}>
              Interactive Task Management
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              View and manage project tasks with our vertical Gantt chart interface
            </Typography>
            <Button
              variant="contained"
              startIcon={<Task />}
              component={Link}
              href={`/projects/${projectId}/tasks`}
              size="large"
            >
              Open Task Manager
            </Button>
          </Box>
        </TabPanel>

        <TabPanel value={tabValue} index={2}>
          <Typography variant="h6" sx={{ mb: 2 }}>Project Team</Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
            {users.slice(0, 10).map((user: any) => (
              <Box key={user.id} sx={{ display: 'flex', alignItems: 'center', gap: 1, p: 1, border: 1, borderColor: 'divider', borderRadius: 1 }}>
                <Avatar sx={{ width: 32, height: 32 }}>
                  {user.name.charAt(0)}
                </Avatar>
                <Box>
                  <Typography variant="body2" sx={{ fontWeight: 'medium' }}>
                    {user.name}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {user.role || 'Team Member'}
                  </Typography>
                </Box>
              </Box>
            ))}
          </Box>
        </TabPanel>

        <TabPanel value={tabValue} index={3}>
          <Typography variant="h6" sx={{ mb: 2 }}>Procurement Overview</Typography>
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              Manage procurement requests and approvals for this project
            </Typography>
            <Button
              variant="contained"
              startIcon={<ShoppingCart />}
              component={Link}
              href={`/projects/${projectId}/procurement`}
            >
              Open Procurement
            </Button>
          </Box>
        </TabPanel>
      </Paper>
    </Box>
  );
}
