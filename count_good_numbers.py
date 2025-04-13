import sys

class Solution(object):
    def countGoodNumbers(self, n):
        """
        :type n: int
        :rtype: int
        """
        MOD = 10**9 + 7
        
        def my_pow(base, exp):
            """使用快速幂算法计算 (base^exp) % MOD"""
            if exp == 0:
                return 1
            if exp == 1:
                return base % MOD
            
            half = my_pow(base, exp // 2)
            if exp % 2 == 0:
                return (half * half) % MOD
            return (half * half * base) % MOD
        
        # 偶数位置可以放0,2,4,6,8，共5个数字
        # 奇数位置可以放2,3,5,7，共4个数字
        even_count = (n + 1) // 2  # 偶数位置的数量
        odd_count = n // 2         # 奇数位置的数量
        
        # 结果是 5^even_count * 4^odd_count
        result = (my_pow(5, even_count) * my_pow(4, odd_count)) % MOD
        return result

# 测试代码
if __name__ == "__main__":
    solution = Solution()
    # 测试用例
    print(f"n = 1: {solution.countGoodNumbers(1)}\n")
    sys.stdout.flush()
    print(f"n = 4: {solution.countGoodNumbers(4)}\n")
    sys.stdout.flush()
    print(f"n = 50: {solution.countGoodNumbers(50)}\n")
    sys.stdout.flush()