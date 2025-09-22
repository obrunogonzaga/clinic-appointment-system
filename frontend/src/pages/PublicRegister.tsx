import { useMemo, useState } from 'react';
import { useNavigate, Navigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useAuth } from '../hooks/useAuth';
import { authService } from '../services/auth';
import type { PublicRegisterData, UserRole } from '../types/auth';

const ROLE_OPTIONS: Array<{ value: Exclude<UserRole, 'admin'>; label: string; description: string }> = [
  {
    value: 'colaborador',
    label: 'Colaborador',
    description: 'Usuários internos que apoiam o atendimento da clínica.',
  },
  {
    value: 'coletor',
    label: 'Coletor',
    description: 'Responsáveis por coletas e entregas operacionais.',
  },
  {
    value: 'motorista',
    label: 'Motorista',
    description: 'Motoristas que realizam o transporte dos pacientes.',
  },
];

const registerSchema = z
  .object({
    name: z.string().min(2, 'Informe seu nome completo'),
    email: z.string().email('Informe um email válido'),
    password: z.string().min(8, 'A senha deve ter ao menos 8 caracteres'),
    confirmPassword: z.string().min(8, 'Confirme sua senha'),
    role: z.enum(['colaborador', 'coletor', 'motorista']),
    phone: z.string().optional(),
    department: z.string().optional(),
    cpf: z.string().optional(),
    drivers_license: z.string().optional(),
  })
  .superRefine((data, ctx) => {
    if (data.password !== data.confirmPassword) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        path: ['confirmPassword'],
        message: 'As senhas precisam ser iguais',
      });
    }

    if (data.role === 'motorista' && !data.drivers_license) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        path: ['drivers_license'],
        message: 'Informe a CNH para cadastro como motorista',
      });
    }
  });

type RegisterFormValues = z.infer<typeof registerSchema>;

export function PublicRegister() {
  const { isAuthenticated, isLoading } = useAuth();
  const navigate = useNavigate();
  const [serverMessage, setServerMessage] = useState<string>('');
  const [serverError, setServerError] = useState<string>('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [pendingApproval, setPendingApproval] = useState<boolean>(false);

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<RegisterFormValues>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      role: 'colaborador',
    },
  });

  const selectedRole = watch('role');

  const roleHelpText = useMemo(() => {
    return ROLE_OPTIONS.find((option) => option.value === selectedRole)?.description ?? '';
  }, [selectedRole]);

  const onSubmit = async (values: RegisterFormValues) => {
    setServerError('');
    setServerMessage('');

    const payload: PublicRegisterData = {
      email: values.email,
      name: values.name,
      password: values.password,
      role: values.role,
      phone: values.phone,
      department: values.department,
      cpf: values.cpf,
      drivers_license: values.role === 'motorista' ? values.drivers_license : undefined,
    };

    try {
      setIsSubmitting(true);
      await authService.publicRegister(payload);
      setPendingApproval(true);
      setServerMessage(
        'Cadastro enviado com sucesso! Enviamos um email de verificação — confirme seu endereço e aguarde a aprovação do administrador.'
      );
    } catch (error: unknown) {
      const apiMessage =
        typeof error === 'object' && error !== null && 'response' in error
          ? (error as { response?: { data?: { detail?: string } } }).response?.data?.detail
          : undefined;
      setServerError(apiMessage || 'Não foi possível concluir o cadastro. Tente novamente em instantes.');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isAuthenticated && !isLoading) {
    return <Navigate to="/" replace />;
  }

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-3xl w-full bg-white shadow rounded-lg overflow-hidden">
        <div className="grid grid-cols-1 md:grid-cols-5">
          <div className="bg-blue-600 text-white p-8 md:col-span-2 flex flex-col justify-between">
            <div>
              <h2 className="text-3xl font-bold">Crie sua conta</h2>
              <p className="mt-4 text-sm text-blue-100">
                Solicite acesso ao sistema informando seu papel na clínica. Após o cadastro, um administrador revisará suas informações.
              </p>
            </div>
            <div className="mt-8 space-y-4 text-sm text-blue-100">
              <div>
                <p className="font-semibold text-white">Como funciona?</p>
                <ul className="mt-2 space-y-1 list-disc list-inside">
                  <li>Envie seus dados utilizando o formulário ao lado.</li>
                  <li>Verifique o email recebido para confirmar sua identidade.</li>
                  <li>Um administrador aprovará sua conta antes do primeiro acesso.</li>
                </ul>
              </div>
              <button
                type="button"
                onClick={() => navigate('/login')}
                className="inline-flex items-center justify-center rounded-md border border-white/40 px-4 py-2 text-sm font-medium text-white hover:bg-white/10 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-blue-600 focus:ring-white"
              >
                Já tenho conta
              </button>
            </div>
          </div>
          <div className="p-8 md:col-span-3">
            <form className="space-y-6" onSubmit={handleSubmit(onSubmit)}>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label htmlFor="name" className="block text-sm font-medium text-gray-700">
                    Nome completo
                  </label>
                  <input
                    id="name"
                    type="text"
                    autoComplete="name"
                    {...register('name')}
                    className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                    placeholder="Maria Silva"
                    disabled={isSubmitting || pendingApproval}
                  />
                  {errors.name && <p className="mt-1 text-sm text-red-600">{errors.name.message}</p>}
                </div>

                <div>
                  <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                    Email corporativo
                  </label>
                  <input
                    id="email"
                    type="email"
                    autoComplete="email"
                    {...register('email')}
                    className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                    placeholder="nome@empresa.com"
                    disabled={isSubmitting || pendingApproval}
                  />
                  {errors.email && <p className="mt-1 text-sm text-red-600">{errors.email.message}</p>}
                </div>

                <div>
                  <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                    Senha
                  </label>
                  <input
                    id="password"
                    type="password"
                    autoComplete="new-password"
                    {...register('password')}
                    className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                    placeholder="Crie uma senha segura"
                    disabled={isSubmitting || pendingApproval}
                  />
                  {errors.password && <p className="mt-1 text-sm text-red-600">{errors.password.message}</p>}
                </div>

                <div>
                  <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700">
                    Confirme a senha
                  </label>
                  <input
                    id="confirmPassword"
                    type="password"
                    autoComplete="new-password"
                    {...register('confirmPassword')}
                    className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                    placeholder="Repita a senha"
                    disabled={isSubmitting || pendingApproval}
                  />
                  {errors.confirmPassword && (
                    <p className="mt-1 text-sm text-red-600">{errors.confirmPassword.message}</p>
                  )}
                </div>

                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700">
                    Qual é o seu papel?
                  </label>
                  <div className="mt-3 space-y-3">
                    {ROLE_OPTIONS.map((option) => (
                      <label
                        key={option.value}
                        className={`flex items-start rounded-md border p-3 cursor-pointer transition ${
                          selectedRole === option.value
                            ? 'border-blue-500 bg-blue-50'
                            : 'border-gray-200 hover:border-blue-300'
                        } ${pendingApproval ? 'opacity-70 cursor-not-allowed' : ''}`}
                      >
                        <input
                          type="radio"
                          value={option.value}
                          className="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500"
                          {...register('role')}
                          disabled={isSubmitting || pendingApproval}
                        />
                        <span className="ml-3">
                          <span className="block text-sm font-medium text-gray-900">{option.label}</span>
                          <span className="block text-sm text-gray-500">{option.description}</span>
                        </span>
                      </label>
                    ))}
                  </div>
                  {roleHelpText && (
                    <p className="mt-2 text-sm text-gray-500">{roleHelpText}</p>
                  )}
                </div>

                <div>
                  <label htmlFor="phone" className="block text-sm font-medium text-gray-700">
                    Telefone (opcional)
                  </label>
                  <input
                    id="phone"
                    type="tel"
                    {...register('phone')}
                    className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                    placeholder="(11) 99999-0000"
                    disabled={isSubmitting || pendingApproval}
                  />
                  {errors.phone && <p className="mt-1 text-sm text-red-600">{errors.phone.message}</p>}
                </div>

                <div>
                  <label htmlFor="department" className="block text-sm font-medium text-gray-700">
                    Setor/Equipe (opcional)
                  </label>
                  <input
                    id="department"
                    type="text"
                    {...register('department')}
                    className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                    placeholder="Central de atendimento"
                    disabled={isSubmitting || pendingApproval}
                  />
                  {errors.department && <p className="mt-1 text-sm text-red-600">{errors.department.message}</p>}
                </div>

                <div>
                  <label htmlFor="cpf" className="block text-sm font-medium text-gray-700">
                    CPF (opcional)
                  </label>
                  <input
                    id="cpf"
                    type="text"
                    {...register('cpf')}
                    className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                    placeholder="000.000.000-00"
                    disabled={isSubmitting || pendingApproval}
                  />
                  {errors.cpf && <p className="mt-1 text-sm text-red-600">{errors.cpf.message}</p>}
                </div>

                {selectedRole === 'motorista' && (
                  <div>
                    <label htmlFor="drivers_license" className="block text-sm font-medium text-gray-700">
                      CNH
                    </label>
                    <input
                      id="drivers_license"
                      type="text"
                      {...register('drivers_license')}
                      className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                      placeholder="Informe sua CNH"
                      disabled={isSubmitting || pendingApproval}
                    />
                    {errors.drivers_license && (
                      <p className="mt-1 text-sm text-red-600">{errors.drivers_license.message}</p>
                    )}
                  </div>
                )}
              </div>

              {serverError && (
                <div className="rounded-md bg-red-50 p-4">
                  <div className="text-sm text-red-800">{serverError}</div>
                </div>
              )}

              {serverMessage && (
                <div className="rounded-md bg-blue-50 p-4">
                  <p className="text-sm text-blue-800">
                    {serverMessage}
                  </p>
                  <ul className="mt-3 text-sm text-blue-700 list-disc list-inside space-y-1">
                    <li>Após a aprovação, você receberá um email de confirmação.</li>
                    <li>Enquanto aguarda, não será possível fazer login.</li>
                    <li>Em caso de urgência, contate o administrador responsável.</li>
                  </ul>
                </div>
              )}

              <button
                type="submit"
                disabled={isSubmitting || pendingApproval}
                className="w-full flex justify-center py-3 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-60 disabled:cursor-not-allowed"
              >
                {isSubmitting ? 'Enviando cadastro...' : pendingApproval ? 'Cadastro enviado' : 'Solicitar acesso'}
              </button>

              <p className="text-sm text-gray-500 text-center">
                Precisando de auxílio? Entre em contato com <a href="mailto:suporte@clinicapp.com.br" className="font-medium text-blue-600 hover:text-blue-500">suporte@clinicapp.com.br</a>.
              </p>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}
