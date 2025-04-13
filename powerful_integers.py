class Solution(object):
    def numberOfPowerfulInt(self, start, finish, limit, s):
        """
        :type start: int
        :type finish: int
        :type limit: int
        :type s: str
        :rtype: int
        """
        def digit_dp(pos, tight, num_str):
            if pos == len(num_str):
                return 1
            
            if pos >= len(num_str) - len(s):
                target = s[pos - (len(num_str) - len(s))]
                if tight and int(num_str[pos]) < int(target):
                    return 0
                if int(target) > limit:
                    return 0
                return digit_dp(pos + 1, tight and int(num_str[pos]) == int(target), num_str)
                
            if (pos, tight) in memo:
                return memo[(pos, tight)]
                
            up = int(num_str[pos]) if tight else limit
            ans = 0
            
            for d in xrange(up + 1):
                if d > limit:
                    break
                ans += digit_dp(pos + 1, tight and d == up, num_str)
                
            memo[(pos, tight)] = ans
            return ans
            
        def count(x):
            if x < int(s):
                return 0
            num_str = str(x)
            if len(s) > len(num_str):
                return 0
            global memo
            memo = {}
            return digit_dp(0, True, num_str)
        
        # 检查后缀s中的数字是否都不超过limit
        if any(int(c) > limit for c in s):
            return 0
            
        return count(finish) - count(start - 1)