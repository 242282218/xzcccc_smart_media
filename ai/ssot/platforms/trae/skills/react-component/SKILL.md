---
name: react-component
description: 设计和实现高质量的 React 组件。
---

# React Component

设计和实现高质量的 React 组件。

## When to Invoke

- 开发新组件
- 重构现有组件
- 优化组件性能
- 设计组件库
- 代码审查

## Input Format

```yaml
component_requirements:
  name: "UserProfile"
  description: "显示用户信息的卡片组件"
  features:
    - "显示头像"
    - "显示用户名"
    - "编辑功能"
    - "加载状态"

design_mock: "user-profile-card.png"
state_complexity: "medium"
```

## Output Format

```yaml
component_code: |
  import React, { useState, useCallback } from 'react';
  import './UserProfile.css';
  
  interface UserProfileProps {
    user: {
      id: string;
      name: string;
      avatar: string;
    };
    onEdit?: (userId: string) => void;
    loading?: boolean;
  }
  
  export const UserProfile: React.FC<UserProfileProps> = ({
    user,
    onEdit,
    loading = false
  }) => {
    const [isEditing, setIsEditing] = useState(false);
    
    const handleEdit = useCallback(() => {
      setIsEditing(true);
      onEdit?.(user.id);
    }, [user.id, onEdit]);
    
    if (loading) {
      return <div className="user-profile-loading">Loading...</div>;
    }
    
    return (
      <div className="user-profile">
        <img src={user.avatar} alt={user.name} />
        <h3>{user.name}</h3>
        <button onClick={handleEdit}>Edit</button>
      </div>
    );
  };

props_interface: |
  interface UserProfileProps {
    user: {
      id: string;
      name: string;
      avatar: string;
    };
    onEdit?: (userId: string) => void;
    loading?: boolean;
  }

test_code: |
  import { render, screen, fireEvent } from '@testing-library/react';
  import { UserProfile } from './UserProfile';
  
  describe('UserProfile', () => {
    const mockUser = {
      id: '1',
      name: 'John Doe',
      avatar: 'avatar.jpg'
    };
    
    it('renders user information', () => {
      render(<UserProfile user={mockUser} />);
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });
    
    it('calls onEdit when edit button clicked', () => {
      const onEdit = jest.fn();
      render(<UserProfile user={mockUser} onEdit={onEdit} />);
      fireEvent.click(screen.getByText('Edit'));
      expect(onEdit).toHaveBeenCalledWith('1');
    });
  });

storybook: |
  export default {
    title: 'Components/UserProfile',
    component: UserProfile
  };
  
  export const Default = () => (
    <UserProfile user={{ id: '1', name: 'John', avatar: 'avatar.jpg' }} />
  );
  
  export const Loading = () => (
    <UserProfile user={{ id: '1', name: 'John', avatar: 'avatar.jpg' }} loading />
  );
```

## Examples

### Example 1: 表单组件

**Input:** 用户注册表单

**Output:**
- 受控组件实现
- 表单验证
- 错误处理
- 提交状态

### Example 2: 列表组件

**Input:** 商品列表

**Output:**
- 虚拟滚动优化
- 分页/无限滚动
- 筛选排序
- 性能优化

## Best Practices

1. **单一职责**: 每个组件只做一件事
2. **Props 明确**: 清晰的 Props 类型定义
3. **状态提升**: 合理的状态管理
4. **性能优化**: 使用 memo、useMemo、useCallback