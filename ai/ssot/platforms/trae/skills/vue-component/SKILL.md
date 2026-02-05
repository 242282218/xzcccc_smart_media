---
name: vue-component
description: 设计和实现高质量的 Vue 组件。
---

# Vue Component

设计和实现高质量的 Vue 组件。

## When to Invoke

- 开发新组件
- 重构现有组件
- 优化组件性能
- 设计组件库
- 代码审查

## Input Format

```yaml
component_requirements:
  name: "UserCard"
  description: "显示用户信息的卡片组件"
  features:
    - "显示头像"
    - "显示用户名"
    - "编辑功能"
    - "加载状态"

vue_version: "3.x"
api_style: "composition"
```

## Output Format

```yaml
component_code: |
  <template>
    <div class="user-card" :class="{ loading }">
      <img :src="user.avatar" :alt="user.name" />
      <h3>{{ user.name }}</h3>
      <button @click="handleEdit">Edit</button>
    </div>
  </template>
  
  <script setup lang="ts">
  import { ref } from 'vue';
  
  interface User {
    id: string;
    name: string;
    avatar: string;
  }
  
  interface Props {
    user: User;
    loading?: boolean;
  }
  
  const props = withDefaults(defineProps<Props>(), {
    loading: false
  });
  
  const emit = defineEmits<{
    edit: [userId: string];
  }>();
  
  const isEditing = ref(false);
  
  const handleEdit = () => {
    isEditing.value = true;
    emit('edit', props.user.id);
  };
  </script>
  
  <style scoped>
  .user-card {
    padding: 16px;
    border: 1px solid #ddd;
    border-radius: 8px;
  }
  
  .user-card.loading {
    opacity: 0.5;
  }
  </style>

props_definition: |
  interface Props {
    user: {
      id: string;
      name: string;
      avatar: string;
    };
    loading?: boolean;
  }

emits_definition: |
  defineEmits<{
    edit: [userId: string];
  }>();

test_code: |
  import { describe, it, expect } from 'vitest';
  import { mount } from '@vue/test-utils';
  import UserCard from './UserCard.vue';
  
  describe('UserCard', () => {
    const mockUser = {
      id: '1',
      name: 'John Doe',
      avatar: 'avatar.jpg'
    };
    
    it('renders user information', () => {
      const wrapper = mount(UserCard, {
        props: { user: mockUser }
      });
      expect(wrapper.text()).toContain('John Doe');
    });
    
    it('emits edit event when button clicked', async () => {
      const wrapper = mount(UserCard, {
        props: { user: mockUser }
      });
      await wrapper.find('button').trigger('click');
      expect(wrapper.emitted('edit')).toBeTruthy();
      expect(wrapper.emitted('edit')[0]).toEqual(['1']);
    });
  });
```

## Examples

### Example 1: 表单组件

**Input:** 用户注册表单

**Output:**
- 双向绑定实现
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

1. **组合式 API**: 优先使用 Composition API
2. **TypeScript**: 使用类型安全的 Props/Emits
3. **样式作用域**: 使用 scoped CSS
4. **性能优化**: 使用 v-memo、computed