import { LockOutlined, UserOutlined } from '@ant-design/icons';
import { App as AntdApp, Alert, Button, Card, Col, Flex, Form, Input, Row, Typography } from 'antd';
import { useEffect } from 'react';
import { Navigate, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '@/features/auth/hooks/useAuth';

interface LoginFormValues {
  username: string;
  password: string;
}

const LoginPage = () => {
  const [form] = Form.useForm<LoginFormValues>();
  const { message } = AntdApp.useApp();
  const navigate = useNavigate();
  const location = useLocation();
  const {
    signIn,
    isAuthenticating,
    isInitialized,
    isAuthenticated,
    error,
    resetError,
  } = useAuth();
  const fromPath = (location.state as { from?: Location })?.from?.pathname ?? '/dashboard';

  useEffect(() => {
    if (isAuthenticated && isInitialized) {
      navigate(fromPath, { replace: true });
    }
  }, [fromPath, isAuthenticated, isInitialized, navigate]);

  if (isInitialized && isAuthenticated) {
    return <Navigate to={fromPath} replace />;
  }

  const handleSubmit = async ({ username, password }: LoginFormValues) => {
    try {
      await signIn(username, password);
      message.success('Welcome back!');
      navigate(fromPath, { replace: true });
    } catch (err) {
      console.error(err);
      message.error('Unable to sign in. Please check your credentials.');
    }
  };

  return (
    <Flex style={{ minHeight: '100vh' }} align="center" justify="center" className="bg-slate-100 p-6">
      <Row gutter={[32, 32]} align="middle" justify="center" style={{ width: '100%', maxWidth: 960 }}>
        <Col xs={24} md={12}>
          <Typography.Title level={2}>Welcome to MTO360</Typography.Title>
          <Typography.Paragraph type="secondary">
            Manage manufacturing, inventory, and sales operations from a unified workspace.
          </Typography.Paragraph>
          <Typography.Paragraph>
            Sign in using your organizational credentials. Access is restricted to authorized personnel.
          </Typography.Paragraph>
        </Col>
        <Col xs={24} md={12}>
          <Card title="Sign in" bordered={false} className="shadow-lg">
            <Form<LoginFormValues> form={form} layout="vertical" onFinish={handleSubmit} requiredMark={false}>
              {error && (
                <Alert
                  type="error"
                  message={error}
                  showIcon
                  closable
                  style={{ marginBottom: 16 }}
                  onClose={resetError}
                />
              )}
              <Form.Item
                name="username"
                label="Username"
                rules={[{ required: true, message: 'Enter your username' }]}
              >
                <Input prefix={<UserOutlined />} placeholder="jane.doe" autoComplete="username" size="large" />
              </Form.Item>
              <Form.Item
                name="password"
                label="Password"
                rules={[{ required: true, message: 'Enter your password' }]}
              >
                <Input.Password
                  prefix={<LockOutlined />}
                  placeholder="••••••••"
                  autoComplete="current-password"
                  size="large"
                />
              </Form.Item>
              <Form.Item>
                <Button
                  type="primary"
                  htmlType="submit"
                  size="large"
                  block
                  loading={isAuthenticating}
                >
                  Sign in
                </Button>
              </Form.Item>
            </Form>
          </Card>
        </Col>
      </Row>
    </Flex>
  );
};

export default LoginPage;
