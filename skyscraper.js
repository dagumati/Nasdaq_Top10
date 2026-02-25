function solution(A) {
    const N = A.length;
    
    // Create array of objects with index and maxHeight
    const buildings = [];
    for (let i = 0; i < N; i++) {
        buildings.push({index: i, maxHeight: A[i]});
    }
    
    // Sort by maxHeight in DESCENDING order
    // This allows buildings with higher constraints to get higher heights
    buildings.sort((a, b) => b.maxHeight - a.maxHeight);
    
    // Create a set to track used heights
    const used = new Set();
    const result = new Array(N);
    
    for (let i = 0; i < N; i++) {
        const building = buildings[i];
        
        // Find the largest unused height within the constraint
        let assignedHeight = building.maxHeight;
        
        // Decrement until we find an unused height
        while (used.has(assignedHeight) && assignedHeight > 0) {
            assignedHeight--;
        }
        
        if (assignedHeight <= 0) {
            throw new Error("No solution exists");
        }
        
        result[building.index] = assignedHeight;
        used.add(assignedHeight);
    }
    
    return result;
}

// Test cases
console.log(solution([1,2,3]));  // [1,2,3]
console.log(solution([9,4,3,7,7]));  // Expected: [9,4,3,7,6] or [9,4,3,6,7]
console.log(solution([2,5,4,5,5]));  // [1,2,3,4,5]

