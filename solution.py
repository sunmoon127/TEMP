class Solution(object):
    def countFairPairs(self, nums, lower, upper):
        """
        :type nums: List[int]
        :type lower: int
        :type upper: int
        :rtype: int
        """
        nums.sort()
        count = 0
        n = len(nums)
        
        for i in range(n-1):
            # 查找满足 lower <= nums[i] + nums[j] <= upper 的右边界
            left = self.binary_search_left(nums, i+1, n-1, lower - nums[i])
            right = self.binary_search_right(nums, i+1, n-1, upper - nums[i])
            
            if left <= right:
                count += right - left + 1
                
        return count
    
    def binary_search_left(self, nums, left, right, target):
        # 查找左边界
        l, r = left, right
        while l <= r:
            mid = l + (r - l) // 2
            if nums[mid] < target:
                l = mid + 1
            else:
                r = mid - 1
        return l
    
    def binary_search_right(self, nums, left, right, target):
        # 查找右边界
        l, r = left, right
        while l <= r:
            mid = l + (r - l) // 2
            if nums[mid] <= target:
                l = mid + 1
            else:
                r = mid - 1
        return r
