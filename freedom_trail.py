from collections import defaultdict

class Solution(object):
    def findRotateSteps(self, ring, key):
        """
        计算拼写key所需的最少步数
        
        Args:
            ring: str, 表示戒指上的字符
            key: str, 需要拼写的字符串
            
        Returns:
            int: 最少需要的步数
        """
        # 预处理：记录ring中每个字符出现的位置
        char_to_pos = defaultdict(list)
        for i, c in enumerate(ring):
            char_to_pos[c].append(i)
            
        def find_min_steps(ring_pos, key_pos, memo):
            if key_pos == len(key):
                return 0
                
            if (ring_pos, key_pos) in memo:
                return memo[(ring_pos, key_pos)]
                
            target = key[key_pos]
            min_steps = float('inf')
            
            for i in char_to_pos[target]:
                dist = abs(i - ring_pos)
                rotate_steps = min(dist, len(ring) - dist)
                
                next_steps = find_min_steps(i, key_pos + 1, memo)
                total_steps = rotate_steps + 1 + next_steps
                min_steps = min(min_steps, total_steps)
            
            memo[(ring_pos, key_pos)] = min_steps
            return min_steps
            
        return find_min_steps(0, 0, {})
