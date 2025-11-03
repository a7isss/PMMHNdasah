'use client';

import React, { useState, useMemo } from 'react';
import { useParams } from 'next/navigation';
import {
  Box,
  Typography,
  Paper,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  IconButton,
  Tooltip,
  Alert,
} from '@mui/material';
import {
  Add,
  Edit,
  Delete,
  PlayArrow,
  CheckCircle,
  Error,
  Schedule,
  PersonAdd,
} from '@mui/icons-material';
import { useGetProjectTasksQuery, useCreateTaskMutation, useUpdateTaskMutation, useDeleteTaskMutation } from '@/lib/api/tasksApi';
import { useGetUsersQuery } from '@/lib/api/usersApi';
import VerticalGanttChart, { Task as GanttTask } from '@/components/VerticalGanttChart';
import { format, addDays } from 'date-fns';

interface TaskFormData {
  name: string;
  description: string;
  priority: 'low' | 'medium' | 'high' | 'critical';
  startDate: string;
  endDate: string;
  duration: number;
  assignedTo: string[];
}

const initialFormData: TaskFormData = {
  name: '',
  description: '',
  priority: 'medium',
  startDate: '',
  endDate: '',
  duration: 1,
  assignedTo: [],
};

export default function ProjectTasksPage() {
  const params = useParams();
  const projectId = params.projectId as string;

  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingTask, setEditingTask] = useState<GanttTask | null>(null);
  const [formData, setFormData] = useState<TaskFormData>(initialFormData);

  // API hooks
  const { data: tasksData, isLoading: tasksLoading, error: tasksError } = useGetProjectTasksQuery(projectId);
  const { data: usersData } = useGetUsersQuery({});
  const [createTask, { isLoading: creating }] = useCreateTaskMutation();
  const [updateTask, { isLoading: updating }] = useUpdateTaskMutation();
  const [deleteTask, { isLoading: deleting }] = useDeleteTaskMutation();

  // Transform tasks for the Gantt chart
  const ganttTasks: GanttTask[] = useMemo(() => {
    if (!tasksData?.data) return [];

    return tasksData.data.map((task: any) => ({
      id: task.id,
      name: task.name,
      description: task.description,
      status: task.status,
      priority: task.priority,
      progressPercentage: task.progress_percentage || 0,
      startDate: new Date(task.start_date),
      endDate: new Date(task.end_date),
      duration: task.duration,
      assignedTo: task.assigned_to?.map((user: any) => ({
        id: user.id,
        name: user.name,
        avatar: user.avatar,
      })),
      dependencies: task.dependencies || [],
      parentTaskId: task.parent_task_id,
      level: task.level || 0,
    }));
  }, [tasksData]);

  // Calculate project dates for Gantt chart
  const projectDates = useMemo(() => {
    if (ganttTasks.length === 0) {
      const today = new Date();
      return {
        start: today,
        end: addDays(today, 30),
      };
    }

    const startDates = ganttTasks.map(task => task.startDate);
    const endDates = ganttTasks.map(task => task.endDate);

    return {
      start: new Date(Math.min(...startDates.map(d => d.getTime()))),
      end: new Date(Math.max(...endDates.map(d => d.getTime()))),
    };
  }, [ganttTasks]);

  const handleOpenDialog = (task?: GanttTask) => {
    if (task) {
      setEditingTask(task);
      setFormData({
        name: task.name,
        description: task.description || '',
        priority: task.priority,
        startDate: format(task.startDate, 'yyyy-MM-dd'),
        endDate: format(task.endDate, 'yyyy-MM-dd'),
        duration: task.duration,
        assignedTo: task.assignedTo?.map(u => u.id) || [],
      });
    } else {
      setEditingTask(null);
      setFormData(initialFormData);
    }
    setDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setDialogOpen(false);
    setEditingTask(null);
    setFormData(initialFormData);
  };

  const handleSubmit = async () => {
    try {
      const taskData = {
        ...formData,
        project_id: projectId,
        start_date: formData.startDate,
        end_date: formData.endDate,
        progress_percentage: 0,
        status: 'not_started',
        assigned_to: formData.assignedTo,
      };

      if (editingTask) {
        await updateTask({
          taskId: editingTask.id,
          ...taskData,
        }).unwrap();
      } else {
        await createTask(taskData).unwrap();
      }

      handleCloseDialog();
    } catch (error) {
      console.error('Failed to save task:', error);
    }
  };

  const handleDeleteTask = async (taskId: string) => {
    if (window.confirm('Are you sure you want to delete this task?')) {
      try {
        await deleteTask(taskId).unwrap();
      } catch (error) {
        console.error('Failed to delete task:', error);
      }
    }
  };

  const handleTaskClick = (task: GanttTask) => {
    handleOpenDialog(task);
  };

  if (tasksLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 400 }}>
        <Typography>Loading tasks...</Typography>
      </Box>
    );
  }

  if (tasksError) {
    return (
      <Alert severity="error" sx={{ m: 2 }}>
        Failed to load tasks. Please try again.
      </Alert>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
          Project Tasks
        </Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => handleOpenDialog()}
          sx={{ borderRadius: 2 }}
        >
          Add Task
        </Button>
      </Box>

      {/* Task Statistics */}
      <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
        <Paper sx={{ p: 2, flex: 1 }}>
          <Typography variant="h6">{ganttTasks.length}</Typography>
          <Typography variant="body2" color="text.secondary">Total Tasks</Typography>
        </Paper>
        <Paper sx={{ p: 2, flex: 1 }}>
          <Typography variant="h6">
            {ganttTasks.filter(t => t.status === 'completed').length}
          </Typography>
          <Typography variant="body2" color="text.secondary">Completed</Typography>
        </Paper>
        <Paper sx={{ p: 2, flex: 1 }}>
          <Typography variant="h6">
            {ganttTasks.filter(t => t.status === 'in_progress').length}
          </Typography>
          <Typography variant="body2" color="text.secondary">In Progress</Typography>
        </Paper>
        <Paper sx={{ p: 2, flex: 1 }}>
          <Typography variant="h6">
            {Math.round(ganttTasks.reduce((sum, t) => sum + t.progressPercentage, 0) / Math.max(ganttTasks.length, 1))}%
          </Typography>
          <Typography variant="body2" color="text.secondary">Avg Progress</Typography>
        </Paper>
      </Box>

      {/* Gantt Chart */}
      <VerticalGanttChart
        tasks={ganttTasks}
        projectStartDate={projectDates.start}
        projectEndDate={projectDates.end}
        onTaskClick={handleTaskClick}
        height={600}
      />

      {/* Task Creation/Edit Dialog */}
      <Dialog open={dialogOpen} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          {editingTask ? 'Edit Task' : 'Create New Task'}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, pt: 1 }}>
            <TextField
              label="Task Name"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              fullWidth
              required
            />

            <TextField
              label="Description"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              multiline
              rows={3}
              fullWidth
            />

            <Box sx={{ display: 'flex', gap: 2 }}>
              <FormControl sx={{ flex: 1 }}>
                <InputLabel>Priority</InputLabel>
                <Select
                  value={formData.priority}
                  onChange={(e) => setFormData({ ...formData, priority: e.target.value as any })}
                  label="Priority"
                >
                  <MenuItem value="low">Low</MenuItem>
                  <MenuItem value="medium">Medium</MenuItem>
                  <MenuItem value="high">High</MenuItem>
                  <MenuItem value="critical">Critical</MenuItem>
                </Select>
              </FormControl>

              <TextField
                label="Duration (days)"
                type="number"
                value={formData.duration}
                onChange={(e) => setFormData({ ...formData, duration: parseInt(e.target.value) || 1 })}
                sx={{ flex: 1 }}
                inputProps={{ min: 1 }}
              />
            </Box>

            <Box sx={{ display: 'flex', gap: 2 }}>
              <TextField
                label="Start Date"
                type="date"
                value={formData.startDate}
                onChange={(e) => setFormData({ ...formData, startDate: e.target.value })}
                sx={{ flex: 1 }}
                InputLabelProps={{ shrink: true }}
                required
              />

              <TextField
                label="End Date"
                type="date"
                value={formData.endDate}
                onChange={(e) => setFormData({ ...formData, endDate: e.target.value })}
                sx={{ flex: 1 }}
                InputLabelProps={{ shrink: true }}
                required
              />
            </Box>

            <FormControl fullWidth>
              <InputLabel>Assigned Team Members</InputLabel>
              <Select
                multiple
                value={formData.assignedTo}
                onChange={(e) => setFormData({ ...formData, assignedTo: e.target.value as string[] })}
                renderValue={(selected) => (
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {selected.map((userId) => {
                      const user = usersData?.data?.find((u: any) => u.id === userId);
                      return (
                        <Chip
                          key={userId}
                          label={user?.name || userId}
                          size="small"
                        />
                      );
                    })}
                  </Box>
                )}
              >
                {usersData?.data?.map((user: any) => (
                  <MenuItem key={user.id} value={user.id}>
                    {user.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Box>
        </DialogContent>
        <DialogActions>
          {editingTask && (
            <Button
              color="error"
              onClick={() => handleDeleteTask(editingTask.id)}
              disabled={deleting}
              sx={{ mr: 'auto' }}
            >
              Delete Task
            </Button>
          )}
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button
            onClick={handleSubmit}
            variant="contained"
            disabled={creating || updating || !formData.name.trim()}
          >
            {editingTask ? 'Update Task' : 'Create Task'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
