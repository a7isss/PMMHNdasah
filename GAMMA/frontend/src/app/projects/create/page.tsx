'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  Box,
  Container,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Alert,
  CircularProgress,
  Stepper,
  Step,
  StepLabel,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material';
import { CloudUpload, ArrowBack } from '@mui/icons-material';
import { useCreateProjectMutation } from '@/lib/api/projectsApi';
import { useAppSelector } from '@/lib/hooks';
import Link from 'next/link';

interface BOQItem {
  id: string;
  description: string;
  quantity: number;
  unit: string;
  rate: number;
  amount: number;
}

const steps = ['Project Details', 'BOQ Import', 'Review & Create'];

export default function CreateProjectPage() {
  const router = useRouter();
  const { user } = useAppSelector((state) => state.auth);
  const [createProject, { isLoading, error }] = useCreateProjectMutation();

  const [activeStep, setActiveStep] = useState(0);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    budgetTotal: '',
    startDate: '',
    endDate: '',
  });

  const [boqItems, setBoqItems] = useState<BOQItem[]>([]);
  const [boqFile, setBoqFile] = useState<File | null>(null);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setBoqFile(file);
      // Parse CSV/Excel file here
      // For now, we'll simulate parsing
      const mockBOQItems: BOQItem[] = [
        {
          id: '1',
          description: 'Excavation work',
          quantity: 100,
          unit: 'm³',
          rate: 50,
          amount: 5000,
        },
        {
          id: '2',
          description: 'Concrete foundation',
          quantity: 50,
          unit: 'm³',
          rate: 150,
          amount: 7500,
        },
        {
          id: '3',
          description: 'Steel reinforcement',
          quantity: 2000,
          unit: 'kg',
          rate: 2.5,
          amount: 5000,
        },
      ];
      setBoqItems(mockBOQItems);

      // Calculate total budget from BOQ
      const totalBudget = mockBOQItems.reduce((sum, item) => sum + item.amount, 0);
      setFormData(prev => ({
        ...prev,
        budgetTotal: totalBudget.toString(),
      }));
    }
  };

  const handleNext = () => {
    setActiveStep((prevStep) => prevStep + 1);
  };

  const handleBack = () => {
    setActiveStep((prevStep) => prevStep - 1);
  };

  const handleSubmit = async () => {
    try {
      const projectData = {
        ...formData,
        budgetTotal: parseFloat(formData.budgetTotal),
        startDate: new Date(formData.startDate).toISOString(),
        endDate: new Date(formData.endDate).toISOString(),
        boqItems,
      };

      await createProject(projectData).unwrap();
      router.push('/');
    } catch (err) {
      // Error is handled by the mutation
    }
  };

  const getStepContent = (step: number) => {
    switch (step) {
      case 0:
        return (
          <Box sx={{ mt: 2 }}>
            <Typography variant="h6" gutterBottom>
              Enter Project Basic Information
            </Typography>
            <TextField
              fullWidth
              label="Project Name"
              name="name"
              value={formData.name}
              onChange={handleInputChange}
              margin="normal"
              required
            />
            <TextField
              fullWidth
              label="Description"
              name="description"
              value={formData.description}
              onChange={handleInputChange}
              margin="normal"
              multiline
              rows={3}
            />
            <TextField
              fullWidth
              label="Start Date"
              name="startDate"
              type="date"
              value={formData.startDate}
              onChange={handleInputChange}
              margin="normal"
              InputLabelProps={{ shrink: true }}
              required
            />
            <TextField
              fullWidth
              label="End Date"
              name="endDate"
              type="date"
              value={formData.endDate}
              onChange={handleInputChange}
              margin="normal"
              InputLabelProps={{ shrink: true }}
              required
            />
          </Box>
        );

      case 1:
        return (
          <Box sx={{ mt: 2 }}>
            <Typography variant="h6" gutterBottom>
              Import Bill of Quantities (BOQ)
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Upload your BOQ file (CSV or Excel) to automatically populate project budget and tasks.
            </Typography>

            <Paper sx={{ p: 3, textAlign: 'center', mb: 2 }}>
              <input
                accept=".csv,.xlsx,.xls"
                style={{ display: 'none' }}
                id="boq-file"
                type="file"
                onChange={handleFileUpload}
              />
              <label htmlFor="boq-file">
                <Button
                  variant="outlined"
                  component="span"
                  startIcon={<CloudUpload />}
                  sx={{ mb: 2 }}
                >
                  Upload BOQ File
                </Button>
              </label>
              {boqFile && (
                <Typography variant="body2" color="primary">
                  File uploaded: {boqFile.name}
                </Typography>
              )}
            </Paper>

            {boqItems.length > 0 && (
              <TableContainer component={Paper}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Description</TableCell>
                      <TableCell align="right">Quantity</TableCell>
                      <TableCell>Unit</TableCell>
                      <TableCell align="right">Rate</TableCell>
                      <TableCell align="right">Amount</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {boqItems.map((item) => (
                      <TableRow key={item.id}>
                        <TableCell>{item.description}</TableCell>
                        <TableCell align="right">{item.quantity}</TableCell>
                        <TableCell>{item.unit}</TableCell>
                        <TableCell align="right">${item.rate}</TableCell>
                        <TableCell align="right">${item.amount.toLocaleString()}</TableCell>
                      </TableRow>
                    ))}
                    <TableRow>
                      <TableCell colSpan={4} align="right">
                        <strong>Total Budget:</strong>
                      </TableCell>
                      <TableCell align="right">
                        <strong>${boqItems.reduce((sum, item) => sum + item.amount, 0).toLocaleString()}</strong>
                      </TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </TableContainer>
            )}
          </Box>
        );

      case 2:
        return (
          <Box sx={{ mt: 2 }}>
            <Typography variant="h6" gutterBottom>
              Review Project Details
            </Typography>

            <Paper sx={{ p: 2, mb: 2 }}>
              <Typography variant="h6" gutterBottom>Project Information</Typography>
              <Typography><strong>Name:</strong> {formData.name}</Typography>
              <Typography><strong>Description:</strong> {formData.description}</Typography>
              <Typography><strong>Duration:</strong> {formData.startDate} to {formData.endDate}</Typography>
              <Typography><strong>Budget:</strong> ${parseFloat(formData.budgetTotal).toLocaleString()}</Typography>
            </Paper>

            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>BOQ Summary</Typography>
              <Typography><strong>Items:</strong> {boqItems.length}</Typography>
              <Typography><strong>Total Value:</strong> ${boqItems.reduce((sum, item) => sum + item.amount, 0).toLocaleString()}</Typography>
            </Paper>

            {error && (
              <Alert severity="error" sx={{ mt: 2 }}>
                {'data' in error && error.data && typeof error.data === 'object' && 'detail' in error.data
                  ? (error.data as any).detail
                  : 'Failed to create project. Please try again.'}
              </Alert>
            )}
          </Box>
        );

      default:
        return null;
    }
  };

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Button
          component={Link}
          href="/"
          startIcon={<ArrowBack />}
          sx={{ mb: 2 }}
        >
          Back to Dashboard
        </Button>
        <Typography variant="h4" component="h1" gutterBottom fontWeight="bold">
          Create New Project
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Import your Bill of Quantities (BOQ) to automatically set up project budget and tasks.
        </Typography>
      </Box>

      <Card>
        <CardContent sx={{ p: 4 }}>
          <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
            {steps.map((label) => (
              <Step key={label}>
                <StepLabel>{label}</StepLabel>
              </Step>
            ))}
          </Stepper>

          {getStepContent(activeStep)}

          <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 4 }}>
            <Button
              disabled={activeStep === 0}
              onClick={handleBack}
            >
              Back
            </Button>
            <Button
              variant="contained"
              onClick={activeStep === steps.length - 1 ? handleSubmit : handleNext}
              disabled={isLoading}
            >
              {isLoading ? (
                <CircularProgress size={24} color="inherit" />
              ) : activeStep === steps.length - 1 ? (
                'Create Project'
              ) : (
                'Next'
              )}
            </Button>
          </Box>
        </CardContent>
      </Card>
    </Container>
  );
}
