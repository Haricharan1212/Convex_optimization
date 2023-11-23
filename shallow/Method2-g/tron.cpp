#include <math.h>
#include <time.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdarg.h>
#include "tron.h"
#define Malloc(type,n) (type *)malloc((n)*sizeof(type))

#ifndef min
template <class T> static inline T min(T x,T y) { return (x<y)?x:y; }
#endif

#ifndef max
template <class T> static inline T max(T x,T y) { return (x>y)?x:y; }
#endif

#ifdef __cplusplus
extern "C" {
#endif

extern double dnrm2_(int *, double *, int *);
extern double ddot_(int *, double *, int *, double *, int *);
extern int daxpy_(int *, double *, double *, int *, double *, int *);
extern int dscal_(int *, double *, double *, int *);

#ifdef __cplusplus
}
#endif

static void default_print(const char *buf)
{
	fputs(buf,stdout);
	fflush(stdout);
}

void TRON::info(const char *fmt,...)
{
	char buf[BUFSIZ];
	va_list ap;
	va_start(ap,fmt);
	vsprintf(buf,fmt,ap);
	va_end(ap);
	(*tron_print_string)(buf);
}

TRON::TRON(const function *fun_obj, double eps, int max_cg_iter, int num_sample, int max_iter, double my_c, int solver_type)
{
	this->fun_obj=const_cast<function *>(fun_obj);
	this->eps=eps;
	this->max_iter=max_iter;
	this->max_cg_iter=max_cg_iter;
	this->num_sample=num_sample;
	this->solver_type=solver_type;
	tron_print_string = default_print;
	printf("iter act fun |g| CG cg_time: line_search_time: time num_data f alpha \n");
}

TRON::~TRON()
{
}

void TRON::tron(double *w, const char *test_file)
{
	int i;

	srand(0);
	double eta = 1e-4;
	
	int n = fun_obj->get_nr_variable();
	int l = fun_obj->get_nr_instance();
	double gnorm1, alpha, f, fnew, actred, gs;
	int cg_iter, search = 1, iter = 1, inc = 1;
	long int num_data = 0;
	int *Hsample = new int[l];
	double *s = new double[n];
	double *sold = new double[n];
	double *r = new double[n];
	double *w_new = new double[n];
	double *g = new double[n];

	for (i=0; i<l; i++)
		Hsample[i] = rand() % num_sample;

	for (i=0; i<n; i++)
	{
		s[i] = 0.0;
		w[i] = 0.0;
		sold[i] = 0.0;
	}
	f = fun_obj->fun(w, &num_data);
	iter = 1;
	fun_obj->grad(w, g, Hsample, iter, num_sample, &num_data);
	
	gnorm1 = dnrm2_(&n, g, &inc);
	double gnorm = gnorm1;

	if (gnorm <= eps*gnorm1)
		search = 0;

	double sTs, soldTs=0.0, cg_alpha, cg_beta, shift_time = 0.0, cg_time, line_search_time, soldTsold = 0.0, golds = 0.0;
	while (iter <= max_iter && search)
	{
		const clock_t begin_time = clock();
                cg_iter = trcg(g, s, r, sold, num_sample,&num_data);
	
                gs = ddot_(&n, g, &inc, s, &inc);
		sTs = ddot_(&n, s, &inc, s, &inc);
		if(iter > 1){
			soldTsold = ddot_(&n, sold, &inc, sold, &inc);
			golds = ddot_(&n, g, &inc, sold, &inc);
			soldTs = ddot_(&n, sold, &inc, s, &inc);
		}
		fun_obj->get_alpha(&cg_alpha, &cg_beta, gs, golds, sTs, s, &soldTsold, sold, soldTs, iter, &num_data);
		

		if(iter > 1){
			for (i=0; i<n; i++)
				s[i] = cg_alpha*s[i] + cg_beta*sold[i];
			gs = cg_alpha*gs + cg_beta*golds;
		}
		else{
			for (i=0; i<n; i++)
				s[i] = cg_alpha*s[i];
			gs = cg_alpha*gs;
		}

                cg_time = float(clock() - begin_time)/CLOCKS_PER_SEC;

		const clock_t line_begin_time = clock();
		alpha = 1;
                while(1)
                {
                        memcpy(w_new, w, sizeof(double)*n);
                        daxpy_(&n, &alpha, s, &inc, w_new, &inc);
                        fnew = fun_obj->fun(w_new,&num_data);
                        actred = f - fnew;
                        if (actred+eta*alpha*gs >= 0)
                                break;
			alpha /= 2;
                }
		line_search_time = float( clock() - line_begin_time)/CLOCKS_PER_SEC;
                memcpy(w, w_new, sizeof(double)*n);
                f = fnew;

		fun_obj->grad(w, g, Hsample, iter+1, num_sample,&num_data);
		gnorm = dnrm2_(&n, g, &inc);

		shift_time += float(clock() - begin_time)/CLOCKS_PER_SEC;
		info("%2d %5.3e %5.3e %5.3e %3d %g %g %.6f %ld %.16f %g\n", iter, actred, f, gnorm, cg_iter, cg_time, line_search_time, shift_time, num_data, f, alpha);
		iter++;

		if (gnorm <= eps*gnorm1)
			break;
	
		if(fabs(actred) <= 1.0e-12*fabs(f))
		{
			printf("actual reduction is too small");
			break;
		}
		if (f < -1.0e+32)
		{
			info("WARNING: f < -1.0e+32\n");
			break;
		}
	}

	delete[] g;
	delete[] r;
	delete[] w_new;
	delete[] s;
	delete[] Hsample;
}

int TRON::trcg(double *g, double *s, double *r, double *sold, int num_sample, long int *num_data)
{
	int i, inc = 1;
	int n = fun_obj->get_nr_variable();
	double one = 1;
	double *d = new double[n];
	double *Hd = new double[n];
	double rTr, rnewTrnew, alpha, beta, cgtol;

	for (i=0; i<n; i++)
	{
		Hd[i] = 0.0;
		sold[i] = -g[i];
		s[i] = 0.0;
		r[i] = -g[i];
		d[i] = r[i];
	}
	
	cgtol = 0.1*dnrm2_(&n, g, &inc);

	int cg_iter = 0;
	rTr = ddot_(&n, r, &inc, r, &inc);
	while (1)
	{
		if (dnrm2_(&n, r, &inc) <= cgtol || cg_iter >= max_cg_iter)
			break;
		cg_iter++;
		fun_obj->sample_Hv(d, Hd, num_data);

		alpha = rTr/ddot_(&n, d, &inc, Hd, &inc);
		daxpy_(&n, &alpha, d, &inc, s, &inc);
		alpha = -alpha;
		daxpy_(&n, &alpha, Hd, &inc, r, &inc);
		rnewTrnew = ddot_(&n, r, &inc, r, &inc);
		beta = rnewTrnew/rTr;
		dscal_(&n, &beta, d, &inc);
		daxpy_(&n, &one, r, &inc, d, &inc);
		rTr = rnewTrnew;
	}
	delete[] d;
	delete[] Hd;

	return(cg_iter);
}

double TRON::norm_inf(int n, double *x)
{
	double dmax = fabs(x[0]);
	for (int i=1; i<n; i++)
		if (fabs(x[i]) >= dmax)
			dmax = fabs(x[i]);
	return(dmax);
}

void TRON::set_print_string(void (*print_string) (const char *buf))
{
	tron_print_string = print_string;
}
