#include <stdio.h>
#include <mpi.h>

int main(int argc, char **argv)
{
    int rank, nproc, mat[4][4], vec[4], loc_row[4], y[4], loc_y = 0;

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

        vec[0]=1; vec[1]=2; vec[2]=3; vec[3]=4;

	printf("Matrix:\n");
        for(int i=0;i<4;i++)
        {
            for(int j=0;j<4;j++)
                printf("%d ", mat[i][j]);
            printf("\n");
        }

	printf("Vector:\n");
        for(int i=0;i<4;i++)
            printf("%d ", vec[i]);
        printf("\n");
    }

    MPI_Bcast(vec, 4, MPI_INT, 0, MPI_COMM_WORLD);



    MPI_Scatter(mat, 4, MPI_INT,
                loc_row, 4, MPI_INT,
                0, MPI_COMM_WORLD);

    for(int i=0;i<4;i++)
        loc_y += loc_row[i] * vec[i];

    printf("Process %d computed y = %d\n", rank, loc_y);

    MPI_Gather(&loc_y, 1, MPI_INT,
               y, 1, MPI_INT,
               0, MPI_COMM_WORLD);

    if(rank == 0)
    {
        printf("Final Vector y:\n");
        for(int i=0;i<4;i++)
            printf("%d ", y[i]);
        printf("\n");
    }

    MPI_Finalize();
    return 0;
}
