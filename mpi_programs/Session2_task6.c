/*Parallel Matrix Row Distribution
Task
Rank 0 has a 4×4 matrix.
Distribute rows using MPI_Scatter.
Each process:
✔ Receives one row
✔ Computes sum of its row
✔ Use MPI_Reduce to compute total matrix sum*/






#include <stdio.h>
#include <mpi.h>

int main(int argc, char **argv)
{
    int rank, nproc, mat[4][4], loc_row[4], loc_sum = 0, t_sum = 0;

    MPI_Init(&argc, &argv);

    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &nproc);

    if(rank == 0)
    {
        int temp[4][4] = {
            {1,2,3,4},
            {5,6,7,8},
            {9,10,11,12},
            {13,14,15,16}
        };

        for(int i=0;i<4;i++)
            for(int j=0;j<4;j++)
                mat[i][j] = temp[i][j];
    }

    MPI_Scatter(mat, 4, MPI_INT,
                loc_row, 4, MPI_INT,
                0, MPI_COMM_WORLD);

    for(int i=0;i<4;i++)
        loc_sum += loc_row[i];

    printf("Process %d Row Sum = %d\n", rank, loc_sum);

    MPI_Reduce(&loc_sum, &t_sum, 1,
               MPI_INT, MPI_SUM,
               0, MPI_COMM_WORLD);

    if(rank == 0)
    {
        printf("Total Matrix Sum = %d\n", t_sum);
    }

    MPI_Finalize();
    return 0;
}
