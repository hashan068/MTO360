import { Flex, Spin } from 'antd';

interface FullScreenLoaderProps {
  message?: string;
}

const FullScreenLoader = ({ message = 'Loading application...' }: FullScreenLoaderProps) => (
  <Flex align="center" justify="center" style={{ minHeight: '100vh' }}>
    <Spin size="large" tip={message} />
  </Flex>
);

export default FullScreenLoader;
