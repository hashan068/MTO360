import { LockOutlined, MailOutlined, UserOutlined } from '@ant-design/icons';
import { App as AntdApp, Button, Checkbox, Divider, Flex, Form, Input, Space, Tabs, Typography } from 'antd';
import { useState, useEffect } from 'react';
import { Navigate, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '@/features/auth/hooks/useAuth';

interface LoginFormValues {
  username: string;
  password: string;
  remember?: boolean;
}

interface SignupFormValues {
  username: string;
  password: string;
  confirmPassword: string;
}

type TabKey = 'login' | 'signup';

const LoginPage = () => {
  const [loginForm] = Form.useForm<LoginFormValues>();
  const [signupForm] = Form.useForm<SignupFormValues>();
  const [activeTab, setActiveTab] = useState<TabKey>('login');
  const { message } = AntdApp.useApp();
  const navigate = useNavigate();
  const location = useLocation();
  const {
    signIn,
    signUp,
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

  const handleLogin = async (values: LoginFormValues) => {
    try {
      await signIn(values.username, values.password);
      message.success('Welcome back!');
      navigate(fromPath, { replace: true });
    } catch (err) {
      console.error(err);
      // Error is handled by the auth store
    }
  };

  const handleSignup = async (values: SignupFormValues) => {
    try {
      await signUp(values.username, values.password);
      message.success('Account created successfully!');
      navigate(fromPath, { replace: true });
    } catch (err) {
      console.error(err);
      // Error is handled by the auth store
    }
  };

  const tabItems = [
    {
      key: 'login',
      label: 'Log in',
      children: (
        <Form<LoginFormValues>
          form={loginForm}
          layout="vertical"
          onFinish={handleLogin}
          requiredMark={false}
          size="large"
        >
          {error && activeTab === 'login' && (
            <div style={{ marginBottom: 16, padding: '12px', background: '#fff2f0', border: '1px solid #ffccc7', borderRadius: '6px', color: '#ff4d4f' }}>
              {error}
            </div>
          )}
          <Form.Item
            name="username"
            label="Username"
            rules={[{ required: true, message: 'Please enter your username' }]}
          >
            <Input
              prefix={<UserOutlined style={{ color: '#bfbfbf' }} />}
              placeholder="Enter your username"
              autoComplete="username"
            />
          </Form.Item>
          <Form.Item
            name="password"
            label="Password"
            rules={[{ required: true, message: 'Please enter your password' }]}
          >
            <Input.Password
              prefix={<LockOutlined style={{ color: '#bfbfbf' }} />}
              placeholder="Enter your password"
              autoComplete="current-password"
            />
          </Form.Item>
          <Form.Item>
            <Flex justify="space-between" align="center">
              <Form.Item name="remember" valuePropName="checked" noStyle>
                <Checkbox>Remember for 30 days</Checkbox>
              </Form.Item>
              <Button type="link" style={{ padding: 0 }}>
                Forgot password?
              </Button>
            </Flex>
          </Form.Item>
          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              block
              loading={isAuthenticating}
              style={{ height: 44, fontSize: 16, fontWeight: 500 }}
            >
              Sign in
            </Button>
          </Form.Item>
          <Divider style={{ margin: '24px 0' }}>Or</Divider>
          <Form.Item>
            <Button
              block
              style={{ height: 44, fontSize: 16 }}
              icon={
                <svg width="18" height="18" viewBox="0 0 18 18" style={{ marginRight: 8 }}>
                  <path
                    fill="#4285F4"
                    d="M17.64 9.2c0-.637-.057-1.251-.164-1.84H9v3.481h4.844c-.209 1.125-.843 2.078-1.796 2.717v2.258h2.908c1.702-1.567 2.684-3.874 2.684-6.615z"
                  />
                  <path
                    fill="#34A853"
                    d="M9 18c2.43 0 4.467-.806 5.965-2.184l-2.908-2.258c-.806.54-1.837.86-3.057.86-2.35 0-4.34-1.587-5.053-3.72H.957v2.332C2.438 15.983 5.482 18 9 18z"
                  />
                  <path
                    fill="#FBBC05"
                    d="M3.947 10.698c-.18-.54-.282-1.117-.282-1.698s.102-1.158.282-1.698V4.97H.957C.348 6.175 0 7.55 0 9s.348 2.825.957 4.03l2.99-2.332z"
                  />
                  <path
                    fill="#EA4335"
                    d="M9 3.58c1.321 0 2.508.454 3.44 1.345l2.582-2.58C13.463.891 11.426 0 9 0 5.482 0 2.438 2.017.957 4.97L3.947 7.302C4.66 5.167 6.65 3.58 9 3.58z"
                  />
                </svg>
              }
            >
              Sign in with Google
            </Button>
          </Form.Item>
        </Form>
      ),
    },
    {
      key: 'signup',
      label: 'Sign up',
      children: (
        <Form<SignupFormValues>
          form={signupForm}
          layout="vertical"
          onFinish={handleSignup}
          requiredMark={false}
          size="large"
        >
          {error && activeTab === 'signup' && (
            <div style={{ marginBottom: 16, padding: '12px', background: '#fff2f0', border: '1px solid #ffccc7', borderRadius: '6px', color: '#ff4d4f' }}>
              {error}
            </div>
          )}
          <Form.Item
            name="username"
            label="Username"
            rules={[
              { required: true, message: 'Please enter your username' },
              { min: 3, message: 'Username must be at least 3 characters' },
            ]}
          >
            <Input
              prefix={<UserOutlined style={{ color: '#bfbfbf' }} />}
              placeholder="Enter your username"
              autoComplete="username"
            />
          </Form.Item>
          <Form.Item
            name="password"
            label="Password"
            rules={[
              { required: true, message: 'Please create a password' },
              { min: 8, message: 'Must be at least 8 characters' },
              {
                pattern: /[!@#$%^&*(),.?":{}|<>]/,
                message: 'Must contain one special character',
              },
            ]}
          >
            <Input.Password
              prefix={<LockOutlined style={{ color: '#bfbfbf' }} />}
              placeholder="Create a password"
              autoComplete="new-password"
            />
          </Form.Item>
          <Form.Item
            name="confirmPassword"
            label="Confirm Password"
            dependencies={['password']}
            rules={[
              { required: true, message: 'Please confirm your password' },
              ({ getFieldValue }) => ({
                validator(_, value) {
                  if (!value || getFieldValue('password') === value) {
                    return Promise.resolve();
                  }
                  return Promise.reject(new Error('Passwords do not match'));
                },
              }),
            ]}
          >
            <Input.Password
              prefix={<LockOutlined style={{ color: '#bfbfbf' }} />}
              placeholder="Confirm your password"
              autoComplete="new-password"
            />
          </Form.Item>
          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              block
              loading={isAuthenticating}
              style={{ height: 44, fontSize: 16, fontWeight: 500 }}
            >
              Get started
            </Button>
          </Form.Item>
          <Divider style={{ margin: '24px 0' }}>Or</Divider>
          <Form.Item>
            <Button
              block
              style={{ height: 44, fontSize: 16 }}
              icon={
                <svg width="18" height="18" viewBox="0 0 18 18" style={{ marginRight: 8 }}>
                  <path
                    fill="#4285F4"
                    d="M17.64 9.2c0-.637-.057-1.251-.164-1.84H9v3.481h4.844c-.209 1.125-.843 2.078-1.796 2.717v2.258h2.908c1.702-1.567 2.684-3.874 2.684-6.615z"
                  />
                  <path
                    fill="#34A853"
                    d="M9 18c2.43 0 4.467-.806 5.965-2.184l-2.908-2.258c-.806.54-1.837.86-3.057.86-2.35 0-4.34-1.587-5.053-3.72H.957v2.332C2.438 15.983 5.482 18 9 18z"
                  />
                  <path
                    fill="#FBBC05"
                    d="M3.947 10.698c-.18-.54-.282-1.117-.282-1.698s.102-1.158.282-1.698V4.97H.957C.348 6.175 0 7.55 0 9s.348 2.825.957 4.03l2.99-2.332z"
                  />
                  <path
                    fill="#EA4335"
                    d="M9 3.58c1.321 0 2.508.454 3.44 1.345l2.582-2.58C13.463.891 11.426 0 9 0 5.482 0 2.438 2.017.957 4.97L3.947 7.302C4.66 5.167 6.65 3.58 9 3.58z"
                  />
                </svg>
              }
            >
              Sign up with Google
            </Button>
          </Form.Item>
        </Form>
      ),
    },
  ];

  return (
    <Flex
      style={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        padding: '24px',
      }}
      align="center"
      justify="center"
    >
      <div
        style={{
          width: '100%',
          maxWidth: 440,
          background: '#ffffff',
          borderRadius: '16px',
          padding: '48px',
          boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
        }}
      >
        {/* Logo/Icon */}
        <div style={{ textAlign: 'center', marginBottom: '32px' }}>
          <div
            style={{
              width: 64,
              height: 64,
              margin: '0 auto 16px',
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              borderRadius: '16px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
            }}
          >
            <Typography.Title level={2} style={{ margin: 0, color: '#fff', fontSize: 32 }}>
              M
            </Typography.Title>
          </div>
          <Typography.Title level={2} style={{ margin: 0, marginBottom: 8 }}>
            {activeTab === 'login' ? 'Log in to your account' : 'Create an account'}
          </Typography.Title>
          <Typography.Text type="secondary" style={{ fontSize: 14 }}>
            {activeTab === 'login'
              ? 'Welcome back! Please enter your details.'
              : 'Start your 30-day free trial.'}
          </Typography.Text>
        </div>

        {/* Tabs */}
        <Tabs
          activeKey={activeTab}
          onChange={(key) => {
            setActiveTab(key as TabKey);
            loginForm.resetFields();
            signupForm.resetFields();
            resetError();
          }}
          items={tabItems}
          style={{ marginBottom: 0 }}
        />

        {/* Footer link */}
        {activeTab === 'login' && (
          <div style={{ textAlign: 'center', marginTop: '24px' }}>
            <Typography.Text type="secondary" style={{ fontSize: 14 }}>
              Don't have an account?{' '}
              <Button
                type="link"
                onClick={() => setActiveTab('signup')}
                style={{ padding: 0, height: 'auto', fontSize: 14 }}
              >
                Sign up
              </Button>
            </Typography.Text>
          </div>
        )}
      </div>
    </Flex>
  );
};

export default LoginPage;
