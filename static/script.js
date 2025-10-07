function calculateGrades() {
    let table = document.getElementById('assessmentTable');
    for (let i=1;i<table.rows.length;i++){
        let row = table.rows[i];
        let total=0,count=0;
        for (let j=1;j<=3;j++){
            let score=parseInt(row.cells[j].innerText)||0;
            total+=score; count++;
        }
        let avg=total/count;
        row.cells[4].innerText=total;
        row.cells[5].innerText=avg.toFixed(2);
        row.cells[6].innerText=gradeFromScore(avg);
    }
}
function gradeFromScore(score){
    if(score>=90) return 'E.E 1';
    if(score>=70) return 'E.E 2';
    if(score>=58) return 'M.E 1';
    if(score>=41) return 'M.E 2';
    if(score>=31) return 'A.E 1';
    if(score>=21) return 'A.E 2';
    if(score>=11) return 'B.E 1';
    return 'B.E 2';
}