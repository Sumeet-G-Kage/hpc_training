/* As discussed during session. 
Practice excercise
1000
p0 = main process
    receiving nloops and calculating total_nloops and perform remaining left over iterations
p1,p2,p3 = take care of 333 by each (iteration task) and send nloops to p0*/




#include <stdio.h>
#include <mpi.h>

int main(int argc, char **argv)
{
    int i, rank, nprocs, count, start, stop, nloops, total_nloops;

    MPI_Init(&argc, &argv);

    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &nprocs);

    // Worker processes (p1, p2, p3)
    if (rank != 0)
    {
        count = 1000 / (nprocs - 1);

        start = (rank - 1) * count;
        stop  = start + count;

        nloops = 0;

        for (i = start; i < stop; ++i)
        {
            ++nloops;
        }

        printf("Process %d performed %d iterations of the loop.\n",
               rank, nloops);

        // send nloops to p0
        MPI_Send(&nloops, 1, MPI_INT, 0, 0, MPI_COMM_WORLD);
    }
    else
    {
        // master process p0
        total_nloops = 0;

        for (i = 1; i < nprocs; ++i)
        {
            MPI_Recv(&nloops, 1, MPI_INT, i, 0,
                     MPI_COMM_WORLD, MPI_STATUS_IGNORE);

            total_nloops += nloops;
        }

        printf("Process 0 received total loops = %d\n", total_nloops);

        // remaining work
        nloops = 0;

        for (i = total_nloops; i < 1000; ++i)
        {
            ++nloops;
        }

        printf("Process 0 performed the remaining %d iterations of the loop\n",
               nloops);
    }

    MPI_Finalize();
    return 0;
}
