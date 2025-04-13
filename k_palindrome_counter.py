from collections import Counter
from math import factorial

class Solution(object):
    def can_form_palindrome(self, digits):
        # 检查一组数字是否能形成回文数
        count = Counter(digits)
        odd_count = sum(1 for v in count.values() if v % 2 == 1)
        return odd_count <= 1

    def get_permutation_count(self, digits):
        # 计算一个数字的不同排列数量
        cnt = Counter(digits)
        denominator = 1
        for v in cnt.values():
            denominator *= factorial(v)
        return factorial(len(digits)) // denominator

    def generate_palindromes(self, n, k):
        """生成长度为n的所有可能k回文数"""
        half_len = n // 2
        start = 10 ** (half_len - 1)
        end = 10 ** half_len
        
        if n % 2 == 0:  # 偶数长度的情况
            for i in range(start, end):
                palindrome = str(i) + str(i)[::-1]
                num = int(palindrome)
                if num % k == 0 and len(str(num)) == n:
                    yield num
        else:  # 奇数长度的情况
            for i in range(start, end):
                half = str(i)
                for mid in range(10):
                    palindrome = half + str(mid) + half[::-1]
                    num = int(palindrome)
                    if len(str(num)) == n and num % k == 0:
                        yield num

    def countGoodIntegers(self, n, k):
        if n == 1:
            return sum(1 for i in range(1, 10) if i % k == 0)
        
        result = 0
        seen = set()
        
        # 遍历所有可能的回文数
        for palindrome in self.generate_palindromes(n, k):
            num_str = str(palindrome)
            if num_str[0] != '0':  # 检查前导零
                # 对每个数字组合只计算一次
                digits = list(num_str)
                key = ''.join(sorted(digits))
                if key not in seen:
                    seen.add(key)
                    # 计算有效排列数（不包含前导零的情况）
                    total = self.get_permutation_count(digits)
                    if '0' in num_str:
                        # 计算以0开头的无效排列数
                        zero_count = num_str.count('0')
                        invalid = (total * zero_count) // len(num_str)
                        total -= invalid
                    result += total
        
        return result

# 测试代码
if __name__ == "__main__":
    solution = Solution()
    print(solution.countGoodIntegers(3, 5))  # 应输出27
    print(solution.countGoodIntegers(1, 4))  # 应输出2
    print(solution.countGoodIntegers(5, 6))  # 应输出2468
