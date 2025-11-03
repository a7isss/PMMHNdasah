'use client';

import React, { useState, useMemo } from 'react';
import {
  Box,
  Paper,
  Typography,
  ToggleButton,
  ToggleButtonGroup,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  LinearProgress,
  Chip,
  IconButton,
  Tooltip,
  Avatar,
  AvatarGroup,
} from '@mui/material';
import {
  ViewList,
  Timeline,
  PlayArrow,
  CheckCircle,
  Error,
  Schedule,
  Person,
  Flag,
} from '@mui/icons-material';
import { format, differenceInDays, addDays, startOfWeek, endOfWeek } from 'date-fns';

export type GanttViewMode = 'wbs' | 'timeline';

export interface Task {
  id: string;
  name: string;
  description?: string;
  status: 'not_started' | 'in_progress' | 'completed' | 'on_hold' | 'cancelled';
  priority: 'low' | 'medium' | 'high' | 'critical';
  progressPercentage: number;
  startDate: Date;
  endDate: Date;
  duration: number; // in days
  assignedTo?: {
    id: string;
    name: string;
    avatar?: string;
  }[];
  dependencies?: string[]; // task IDs
  parentTaskId?: string; // for subtasks
  level: number; // indentation level for WBS
}

interface VerticalGanttChartProps {
  tasks: Task[];
  projectStartDate: Date;
  projectEndDate: Date;
  onTaskClick?: (task: Task) => void;
  onTaskUpdate?: (taskId: string, updates: Partial<Task>) => void;
  height?: number;
}

const STATUS_CONFIG = {
  not_started: { color: '#9e9e9e', icon: Schedule, label: 'Not Started' },
  in_progress: { color: '#2196f3', icon: PlayArrow, label: 'In Progress' },
  completed: { color: '#4caf50', icon: CheckCircle, label: 'Completed' },
  on_hold: { color: '#ff9800', icon: Error, label: 'On Hold' },
  cancelled: { color: '#f44336', icon: Error, label: 'Cancelled' },
};

const PRIORITY_CONFIG = {
  low: { color: '#4caf50', label: 'Low' },
  medium: { color: '#ff9800', label: 'Medium' },
  high: { color: '#f44336', label: 'High' },
  critical: { color: '#9c27b0', label: 'Critical' },
};

export default function VerticalGanttChart({
  tasks,
  projectStartDate,
  projectEndDate,
  onTaskClick,
  onTaskUpdate,
  height = 600,
}: VerticalGanttChartProps) {
  const [viewMode, setViewMode] = useState<GanttViewMode>('wbs');

  // Calculate timeline metrics
  const totalProjectDays = differenceInDays(projectEndDate, projectStartDate) + 1;
  const weeks = useMemo(() => {
    const weeksArray = [];
    let currentWeek = startOfWeek(projectStartDate, { weekStartsOn: 1 }); // Monday start

    while (currentWeek <= endOfWeek(projectEndDate, { weekStartsOn: 1 })) {
      weeksArray.push({
        start: currentWeek,
        end: endOfWeek(currentWeek, { weekStartsOn: 1 }),
        label: format(currentWeek, 'MMM dd'),
      });
      currentWeek = addDays(currentWeek, 7);
    }

    return weeksArray;
  }, [projectStartDate, projectEndDate]);

  const getTaskPosition = (task: Task) => {
    const taskStartOffset = differenceInDays(task.startDate, projectStartDate);
    const taskDuration = task.duration;
    const percentage = (taskStartOffset / totalProjectDays) * 100;
    const widthPercentage = (taskDuration / totalProjectDays) * 100;

    return {
      left: `${Math.max(0, percentage)}%`,
      width: `${Math.min(100 - percentage, widthPercentage)}%`,
    };
  };

  const getStatusIcon = (status: Task['status']) => {
    const config = STATUS_CONFIG[status];
    const IconComponent = config.icon;
    return <IconComponent sx={{ color: config.color, fontSize: 16 }} />;
  };

  const getPriorityChip = (priority: Task['priority']) => {
    const config = PRIORITY_CONFIG[priority];
    return (
      <Chip
        size="small"
        label={config.label}
        sx={{
          backgroundColor: config.color,
          color: 'white',
          fontSize: '0.7rem',
          height: '20px',
        }}
      />
    );
  };

  const renderWBSView = () => (
    <TableContainer component={Paper} sx={{ maxHeight: height }}>
      <Table stickyHeader size="small">
        <TableHead>
          <TableRow>
            <TableCell sx={{ fontWeight: 'bold', minWidth: 300 }}>Task Name</TableCell>
            <TableCell sx={{ fontWeight: 'bold', width: 100 }}>Status</TableCell>
            <TableCell sx={{ fontWeight: 'bold', width: 80 }}>Priority</TableCell>
            <TableCell sx={{ fontWeight: 'bold', width: 120 }}>Assigned To</TableCell>
            <TableCell sx={{ fontWeight: 'bold', width: 100 }}>Progress</TableCell>
            <TableCell sx={{ fontWeight: 'bold', width: 150 }}>Time Range</TableCell>
            <TableCell sx={{ fontWeight: 'bold', minWidth: 200 }}>Progress Bar</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {tasks.map((task) => (
            <TableRow
              key={task.id}
              hover
              onClick={() => onTaskClick?.(task)}
              sx={{
                cursor: onTaskClick ? 'pointer' : 'default',
                '&:hover': { backgroundColor: 'action.hover' }
              }}
            >
              <TableCell>
                <Box sx={{ display: 'flex', alignItems: 'center', pl: task.level * 2 }}>
                  {task.level > 0 && <Box sx={{ width: 16, height: 1, backgroundColor: 'divider', mr: 1 }} />}
                  <Typography variant="body2" sx={{ fontWeight: task.level === 0 ? 'bold' : 'normal' }}>
                    {task.name}
                  </Typography>
                </Box>
                {task.description && (
                  <Typography variant="caption" color="text.secondary" sx={{ pl: task.level * 2 + 2 }}>
                    {task.description}
                  </Typography>
                )}
              </TableCell>
              <TableCell>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                  {getStatusIcon(task.status)}
                  <Typography variant="caption">
                    {STATUS_CONFIG[task.status].label}
                  </Typography>
                </Box>
              </TableCell>
              <TableCell>
                {getPriorityChip(task.priority)}
              </TableCell>
              <TableCell>
                {task.assignedTo && task.assignedTo.length > 0 ? (
                  <AvatarGroup max={3} sx={{ justifyContent: 'flex-start' }}>
                    {task.assignedTo.map((user) => (
                      <Tooltip key={user.id} title={user.name}>
                        <Avatar
                          sx={{ width: 24, height: 24, fontSize: '0.75rem' }}
                          src={user.avatar}
                        >
                          {user.name.charAt(0)}
                        </Avatar>
                      </Tooltip>
                    ))}
                  </AvatarGroup>
                ) : (
                  <Typography variant="caption" color="text.secondary">Unassigned</Typography>
                )}
              </TableCell>
              <TableCell>
                <Typography variant="body2">{task.progressPercentage}%</Typography>
              </TableCell>
              <TableCell>
                <Typography variant="caption">
                  {format(task.startDate, 'MMM dd')} - {format(task.endDate, 'MMM dd')}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {task.duration} days
                </Typography>
              </TableCell>
              <TableCell>
                <Box sx={{ width: '100%', position: 'relative' }}>
                  <LinearProgress
                    variant="determinate"
                    value={task.progressPercentage}
                    sx={{
                      height: 8,
                      borderRadius: 4,
                      backgroundColor: 'grey.200',
                      '& .MuiLinearProgress-bar': {
                        backgroundColor: STATUS_CONFIG[task.status].color,
                        borderRadius: 4,
                      },
                    }}
                  />
                  <Box
                    sx={{
                      position: 'absolute',
                      top: 0,
                      left: 0,
                      right: 0,
                      bottom: 0,
                      backgroundColor: 'rgba(255,255,255,0.8)',
                      borderRadius: 4,
                    }}
                  />
                </Box>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );

  const renderTimelineView = () => (
    <Box sx={{ height, overflow: 'auto', position: 'relative' }}>
      {/* Timeline Header */}
      <Box sx={{ position: 'sticky', top: 0, zIndex: 10, backgroundColor: 'background.paper', borderBottom: 1, borderColor: 'divider' }}>
        <Box sx={{ display: 'flex', p: 2, borderBottom: 1, borderColor: 'divider' }}>
          <Box sx={{ width: 300, fontWeight: 'bold' }}>Task</Box>
          <Box sx={{ flex: 1, display: 'flex' }}>
            {weeks.map((week, index) => (
              <Box
                key={index}
                sx={{
                  flex: 1,
                  textAlign: 'center',
                  fontSize: '0.75rem',
                  fontWeight: 'bold',
                  color: 'text.secondary',
                  borderRight: index < weeks.length - 1 ? 1 : 0,
                  borderColor: 'divider',
                  py: 1,
                }}
              >
                {week.label}
              </Box>
            ))}
          </Box>
        </Box>
      </Box>

      {/* Tasks */}
      <Box>
        {tasks.map((task) => (
          <Box
            key={task.id}
            sx={{
              display: 'flex',
              borderBottom: 1,
              borderColor: 'divider',
              minHeight: 60,
              '&:hover': { backgroundColor: 'action.hover' },
              cursor: onTaskClick ? 'pointer' : 'default',
            }}
            onClick={() => onTaskClick?.(task)}
          >
            {/* Task Info */}
            <Box sx={{ width: 300, p: 2, borderRight: 1, borderColor: 'divider' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                {getStatusIcon(task.status)}
                <Typography variant="body2" sx={{ fontWeight: 'medium' }}>
                  {task.name}
                </Typography>
                {getPriorityChip(task.priority)}
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                {task.assignedTo && task.assignedTo.length > 0 ? (
                  <AvatarGroup max={2}>
                    {task.assignedTo.map((user) => (
                      <Avatar key={user.id} sx={{ width: 20, height: 20, fontSize: '0.7rem' }}>
                        {user.name.charAt(0)}
                      </Avatar>
                    ))}
                  </AvatarGroup>
                ) : (
                  <Person sx={{ fontSize: 16, color: 'text.secondary' }} />
                )}
                <Typography variant="caption" color="text.secondary">
                  {task.progressPercentage}% • {task.duration}d
                </Typography>
              </Box>
            </Box>

            {/* Timeline Visualization */}
            <Box sx={{ flex: 1, position: 'relative', display: 'flex' }}>
              {weeks.map((week, index) => (
                <Box
                  key={index}
                  sx={{
                    flex: 1,
                    borderRight: index < weeks.length - 1 ? 1 : 0,
                    borderColor: 'divider',
                    position: 'relative',
                  }}
                >
                  {/* Task bar positioned within this week */}
                  {task.startDate <= week.end && task.endDate >= week.start && (
                    <Box
                      sx={{
                        position: 'absolute',
                        top: 8,
                        height: 16,
                        backgroundColor: STATUS_CONFIG[task.status].color,
                        borderRadius: 1,
                        opacity: 0.8,
                        cursor: 'pointer',
                        '&:hover': { opacity: 1 },
                        boxShadow: 1,
                      }}
                      style={getTaskPosition(task)}
                      title={`${task.name} (${task.progressPercentage}% complete)`}
                    >
                      <Box
                        sx={{
                          height: '100%',
                          width: `${task.progressPercentage}%`,
                          backgroundColor: 'rgba(255,255,255,0.3)',
                          borderRadius: 1,
                        }}
                      />
                    </Box>
                  )}
                </Box>
              ))}
            </Box>
          </Box>
        ))}
      </Box>
    </Box>
  );

  return (
    <Box>
      {/* View Mode Toggle */}
      <Box sx={{ mb: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
          Project Tasks
        </Typography>
        <ToggleButtonGroup
          value={viewMode}
          exclusive
          onChange={(_, newMode) => newMode && setViewMode(newMode)}
          size="small"
        >
          <ToggleButton value="wbs">
            <ViewList sx={{ mr: 1 }} />
            WBS View
          </ToggleButton>
          <ToggleButton value="timeline">
            <Timeline sx={{ mr: 1 }} />
            Timeline View
          </ToggleButton>
        </ToggleButtonGroup>
      </Box>

      {/* Chart Content */}
      {viewMode === 'wbs' ? renderWBSView() : renderTimelineView()}

      {/* Legend */}
      <Box sx={{ mt: 2, p: 2, backgroundColor: 'grey.50', borderRadius: 1 }}>
        <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 'bold' }}>
          Legend
        </Typography>
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
          {Object.entries(STATUS_CONFIG).map(([status, config]) => (
            <Box key={status} sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
              <config.icon sx={{ color: config.color, fontSize: 16 }} />
              <Typography variant="caption">{config.label}</Typography>
            </Box>
          ))}
        </Box>
      </Box>
    </Box>
  );
}
