// MongoDB initialization script
// This script runs when the MongoDB container is first created

// Switch to the clinic database
db = db.getSiblingDB('clinic_db');

// Create collections with schema validation
db.createCollection('users', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['username', 'email', 'password_hash', 'role', 'created_at'],
      properties: {
        username: {
          bsonType: 'string',
          description: 'Must be a string and is required'
        },
        email: {
          bsonType: 'string',
          pattern: '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$',
          description: 'Must be a valid email address'
        },
        password_hash: {
          bsonType: 'string',
          description: 'Hashed password is required'
        },
        role: {
          enum: ['admin', 'doctor', 'nurse', 'receptionist'],
          description: 'Role must be one of the allowed values'
        },
        is_active: {
          bsonType: 'bool',
          description: 'User active status'
        },
        created_at: {
          bsonType: 'date',
          description: 'Creation timestamp'
        },
        updated_at: {
          bsonType: ['date', 'null'],
          description: 'Last update timestamp'
        }
      }
    }
  }
});

db.createCollection('patients', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['name', 'email', 'phone', 'created_at'],
      properties: {
        name: {
          bsonType: 'string',
          minLength: 2,
          maxLength: 100,
          description: 'Patient full name'
        },
        email: {
          bsonType: 'string',
          pattern: '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$',
          description: 'Valid email address'
        },
        phone: {
          bsonType: 'string',
          pattern: '^[0-9]{10,15}$',
          description: 'Phone number (digits only)'
        },
        date_of_birth: {
          bsonType: 'date',
          description: 'Patient date of birth'
        },
        address: {
          bsonType: 'object',
          properties: {
            street: { bsonType: 'string' },
            city: { bsonType: 'string' },
            state: { bsonType: 'string' },
            zip_code: { bsonType: 'string' }
          }
        },
        medical_record_number: {
          bsonType: 'string',
          description: 'External medical record number'
        },
        created_at: {
          bsonType: 'date',
          description: 'Creation timestamp'
        },
        updated_at: {
          bsonType: ['date', 'null'],
          description: 'Last update timestamp'
        }
      }
    }
  }
});

db.createCollection('appointments', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['nome_unidade', 'nome_marca', 'nome_paciente', 'data_agendamento', 'hora_agendamento', 'created_at'],
      properties: {
        id: {
          bsonType: 'string',
          description: 'Unique appointment identifier'
        },
        nome_unidade: {
          bsonType: 'string',
          description: 'Nome da Unidade de Saúde'
        },
        nome_marca: {
          bsonType: 'string',
          description: 'Nome da Marca/Clínica'
        },
        nome_paciente: {
          bsonType: 'string',
          description: 'Nome completo do paciente'
        },
        data_agendamento: {
          bsonType: 'date',
          description: 'Data do agendamento'
        },
        hora_agendamento: {
          bsonType: 'string',
          pattern: '^([0-1][0-9]|2[0-3]):[0-5][0-9]$',
          description: 'Hora do agendamento (HH:MM)'
        },
        tipo_consulta: {
          bsonType: ['string', 'null'],
          description: 'Tipo de consulta médica'
        },
        status: {
          enum: ['Confirmado', 'Cancelado', 'Reagendado', 'Concluído', 'Não Compareceu'],
          description: 'Status do agendamento'
        },
        telefone: {
          bsonType: ['string', 'null'],
          description: 'Telefone de contato do paciente'
        },
        observacoes: {
          bsonType: ['string', 'null'],
          description: 'Observações adicionais'
        },
        created_at: {
          bsonType: 'date',
          description: 'Creation timestamp'
        },
        updated_at: {
          bsonType: ['date', 'null'],
          description: 'Last update timestamp'
        }
      }
    }
  }
});

// Create indexes for better query performance
db.users.createIndex({ 'email': 1 }, { unique: true });
db.users.createIndex({ 'username': 1 }, { unique: true });
db.users.createIndex({ 'role': 1 });

db.patients.createIndex({ 'email': 1 }, { unique: true });
db.patients.createIndex({ 'phone': 1 });
db.patients.createIndex({ 'name': 'text' });

db.appointments.createIndex({ 'nome_unidade': 1 });
db.appointments.createIndex({ 'nome_marca': 1 });
db.appointments.createIndex({ 'nome_paciente': 'text' });
db.appointments.createIndex({ 'data_agendamento': 1 });
db.appointments.createIndex({ 'status': 1 });
db.appointments.createIndex({ 'data_agendamento': 1, 'status': 1 });
db.appointments.createIndex({ 'nome_unidade': 1, 'nome_marca': 1 });
db.appointments.createIndex({ 'id': 1 }, { unique: true, name: 'appointment_id_unique' });

// Create a default admin user (password: admin123)
// Note: In production, change this password immediately
db.users.insertOne({
  username: 'admin',
  email: 'admin@clinicapp.com.br',
  password_hash: '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNiLXCfiyB/yK',
  role: 'admin',
  is_active: true,
  created_at: new Date(),
  updated_at: new Date()
});

print('MongoDB initialization completed successfully!');