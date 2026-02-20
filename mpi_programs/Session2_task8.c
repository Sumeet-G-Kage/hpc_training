/*Parallel Maximum of Matrix
Task
Each process finds local max of its row.
Use:
MPI_Reduce(..., MPI_MAX, ...)
Rank 0 prints global maximum.*/






#include <stdio.h>
#include <mpi.h>

int main(int argc, char **argv)
{
    int rank, nproc;
    int mat[4][4];
    int loc_row[4];
    int loc_max, g_max;

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

        printf("Matrix:\n");
        for(int i=0;i<4;i++)
        {
            for(int j=0;j<4;j++)
                printf("%d ", mat[i][j]);
            printf("\n");
        }
    }

    MPI_Scatter(mat, 4, MPI_INT,
                loc_row, 4, MPI_INT,
                0, MPI_COMM_WORLD);

    loc_max = loc_row[0];

    for(int i=1;i<4;i++)
    {
        if(loc_row[i] > loc_max)
            loc_max = loc_row[i];
    }

    printf("Process %d local max = %d\n", rank, loc_max);

    MPI_Reduce(&loc_max, &g_max, 1,
               MPI_INT, MPI_MAX,
               0, MPI_COMM_WORLD);

    if(rank == 0)
    {
        printf("\nGlobal Maximum = %d\n", g_max);
    }

    MPI_Finalize();
    return 0;
}
