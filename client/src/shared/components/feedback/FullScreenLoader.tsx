import { Spin } from 'antd';

interface FullScreenLoaderProps {
  message?: string;
}

const FullScreenLoader = ({ message = 'Loading application...' }: FullScreenLoaderProps) => (
  <Spin size="large" tip={message} style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
    <div style={{ minHeight: '100vh' }} />
  </Spin>
);

export default FullScreenLoader;

